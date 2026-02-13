-- readonly 계정
CREATE USER IF NOT EXISTS 'mindfit_ro'@'%' IDENTIFIED BY 'mindfit_ro_pass';
GRANT SELECT ON mindfit_db.* TO 'mindfit_ro'@'%';

FLUSH PRIVILEGES;
