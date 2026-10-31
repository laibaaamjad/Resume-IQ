#!/bin/bash
# Runs once, on the first start of an empty MySQL data volume.
# The official mysql image already created the database $MYSQL_DATABASE (resumeiq).
set -e

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
  -- Application account (read + write)
  CREATE USER IF NOT EXISTS 'resumeiq_app'@'%' IDENTIFIED BY '${APP_DB_PASSWORD}';
  GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
    ON \`${MYSQL_DATABASE}\`.* TO 'resumeiq_app'@'%';

  -- Read-only account for the evaluation script
  CREATE USER IF NOT EXISTS 'evaluator'@'%' IDENTIFIED BY '${EVALUATOR_DB_PASSWORD}';
  GRANT SELECT ON \`${MYSQL_DATABASE}\`.* TO 'evaluator'@'%';

  FLUSH PRIVILEGES;
EOSQL
