-- Stop replication on slave1
SELECT pg_promote();

-- Check if promotion successful
SELECT pg_is_in_recovery();