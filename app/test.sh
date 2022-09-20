#!/bin/bash

TEST_DB_PATH="$(pwd)/database/test.db"
if [ -f $TEST_DB_PATH ] ; then
    rm $TEST_DB_PATH
fi

echo $TEST_DB_PATH
touch $TEST_DB_PATH

sqlite3 $TEST_DB_PATH < "$(pwd)/database/scripts/create_database_tables.sql"

echo "Created tables. Inserting user data."

sqlite3 $TEST_DB_PATH "INSERT INTO ref_usertype (type) VALUES ('user')"
sqlite3 $TEST_DB_PATH "INSERT INTO ref_usertype (type) VALUES ('user')"
sqlite3 $TEST_DB_PATH "INSERT INTO ref_usertype (type) VALUES ('admin')"
sqlite3 $TEST_DB_PATH "INSERT INTO ref_usertype (type) VALUES ('superadmin')"
sqlite3 $TEST_DB_PATH "INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (1,'testadmin', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, julianday('now'), julianday('now'), 1, 2)"
sqlite3 $TEST_DB_PATH "INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (2,'testuser', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 1, julianday('now'), julianday('now'), 1, 1)"

echo "Successfully inserted test data. Running test with pytest..."

LOGGING_DATABASE_PATH=$TEST_DB_PATH LOGGING_SECRET=`openssl rand -hex 32` pytest "$(pwd)/test.py"

echo "Testing finished. Clearing up.."

rm $TEST_DB_PATH

echo "Successfully cleared up. Exiting"