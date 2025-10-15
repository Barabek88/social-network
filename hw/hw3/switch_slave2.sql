-- Stop current replication
SELECT pg_promote();

-- Wait a moment
SELECT pg_sleep(2);

-- primary_conninfo = 'host=slave1_host port=5432 user=replication_user'