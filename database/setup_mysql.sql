-- Run once as the MySQL admin (on EC2: `sudo mysql < setup_mysql.sql`; on RDS: mysql -h <endpoint> -u admin -p < setup_mysql.sql)
-- Change the passwords before running.

CREATE DATABASE IF NOT EXISTS resumeiq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Account used by the application (read + write)
CREATE USER IF NOT EXISTS 'resumeiq_app'@'%' IDENTIFIED BY 'CHANGE_ME_APP_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
  ON resumeiq.* TO 'resumeiq_app'@'%';

-- Read-only account for the professor's evaluation script (SELECT only)
CREATE USER IF NOT EXISTS 'evaluator'@'%' IDENTIFIED BY 'CHANGE_ME_READONLY_PASSWORD';
GRANT SELECT ON resumeiq.* TO 'evaluator'@'%';

FLUSH PRIVILEGES;

-- Verify
SHOW GRANTS FOR 'evaluator'@'%';