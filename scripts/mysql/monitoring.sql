-- 1) 현재 세션/커넥션 확인
SHOW PROCESSLIST;

-- 2) InnoDB 상태(락/데드락 단서)
SHOW ENGINE INNODB STATUS;

-- 3) 슬로우 쿼리 로그가 켜져 있는지
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
