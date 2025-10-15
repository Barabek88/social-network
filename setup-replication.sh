#!/bin/bash

echo "Setting up PostgreSQL streaming replication..."

# 1. Start master
echo "Starting master..."
docker-compose up -d db

# Wait for master to be ready
echo "Waiting for master to be ready..."
sleep 10

# 2. Create replication user on master
echo "Creating replication user..."
docker exec postgres-master psql -U postgres -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';"

# 3. Stop slaves if running
echo "Stopping slaves..."
docker-compose stop db-slave1 db-slave2

# 4. Remove slave data directories
echo "Cleaning slave data..."
sudo rm -rf ../.db_data/slave1data/*
sudo rm -rf ../.db_data/slave2data/*

# 5. Create single base backup
echo "Creating base backup..."
docker exec postgres-master pg_basebackup -h localhost -D /tmp/base_backup -U replicator -W -v -P -R

# 6. Copy backup to both slaves
echo "Copying backup to slave1..."
docker cp postgres-master:/tmp/base_backup/. ../.db_data/slave1data/

echo "Copying backup to slave2..."
docker cp postgres-master:/tmp/base_backup/. ../.db_data/slave2data/

# 7. Configure slaves
echo "Configuring slave1..."
echo "primary_conninfo = 'host=postgres-master port=5432 user=replicator password=replicator_password'" >> ../.db_data/slave1data/postgresql.auto.conf
echo "hot_standby = on" >> ../.db_data/slave1data/postgresql.auto.conf
# Create standby.signal file (required for PostgreSQL 12+)
touch ../.db_data/slave1data/standby.signal

echo "Configuring slave2..."
echo "primary_conninfo = 'host=postgres-master port=5432 user=replicator password=replicator_password'" >> ../.db_data/slave2data/postgresql.auto.conf
echo "hot_standby = on" >> ../.db_data/slave2data/postgresql.auto.conf
# Create standby.signal file (required for PostgreSQL 12+)
touch ../.db_data/slave2data/standby.signal

# 8. Start slaves
echo "Starting slaves..."
docker-compose up -d db-slave1 db-slave2

echo "Replication setup complete!"
echo "Master: localhost:5432"
echo "Slave1: localhost:5433"  
echo "Slave2: localhost:5434"