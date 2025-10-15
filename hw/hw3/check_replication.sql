-- Check if in recovery mode (should be true for slave)
SELECT pg_is_in_recovery();

-- Check replication status
SELECT * FROM pg_stat_wal_receiver;