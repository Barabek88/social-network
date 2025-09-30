CREATE INDEX IF NOT EXISTS idx_users_first_name_second_name ON users(first_name, second_name);

DROP INDEX idx_users_search_lower


CREATE INDEX idx_users_search_lower ON users 
(lower(first_name) varchar_pattern_ops, lower(second_name) varchar_pattern_ops);

CREATE INDEX IF NOT EXISTS idx_users_first_name_second_name ON users(lower(first_name), lower(second_name));

SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'users';

SELECT pg_stat_reset();

explain
SELECT id, first_name, second_name, birthdate::date as birthdate, biography, city
FROM users
WHERE lower(first_name) LIKE lower('нау') || '%' and lower(second_name) LIKE lower('кудр') || '%'
order by id


 