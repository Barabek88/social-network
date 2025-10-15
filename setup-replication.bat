@echo off
echo Setting up PostgreSQL streaming replication...

REM 1. Start master
echo Starting master...
docker-compose up -d db

REM Wait for master to be ready
echo Waiting for master to be ready...
timeout /t 10 /nobreak >nul

REM 2. Create replication user on master
echo Creating replication user...
docker exec postgres-master psql -U postgres -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '1';"

REM 3. Stop slaves if running
echo Stopping slaves...
docker-compose stop db-slave1 db-slave2

REM 4. Remove slave data directories
echo Cleaning slave data...
if exist "..\.db_data\slave1data" rmdir /s /q "..\.db_data\slave1data"
if exist "..\.db_data\slave2data" rmdir /s /q "..\.db_data\slave2data"
mkdir "..\.db_data\slave1data"
mkdir "..\.db_data\slave2data"

REM 5. Create single base backup
echo Creating base backup...
docker exec -e PGPASSWORD=1 postgres-master pg_basebackup -h localhost -D /tmp/base_backup -U replicator -v -P -R

REM 6. Copy backup to both slaves
echo Copying backup to slave1...
docker cp postgres-master:/tmp/base_backup/. ../.db_data/slave1data/

echo Copying backup to slave2...
docker cp postgres-master:/tmp/base_backup/. ../.db_data/slave2data/

REM 7. Configure slaves
echo Configuring slave1...
echo primary_conninfo = 'host=postgres-master port=5432 user=replicator password=1 application_name=postgres_slave1' >> "..\.db_data\slave1data\postgresql.auto.conf"
echo hot_standby = on >> "..\.db_data\slave1data\postgresql.auto.conf"
REM standby.signal already created by pg_basebackup -R

echo Configuring slave2...
echo primary_conninfo = 'host=postgres-master port=5432 user=replicator password=1 application_name=postgres_slave2' >> "..\.db_data\slave2data\postgresql.auto.conf"
echo hot_standby = on >> "..\.db_data\slave2data\postgresql.auto.conf"
REM standby.signal already created by pg_basebackup -R

REM 8. Start slaves
echo Starting slaves...
docker-compose up -d db-slave1 db-slave2

echo Replication setup complete!
echo Master: localhost:5432
echo Slave1: localhost:5433
echo Slave2: localhost:5434

pause