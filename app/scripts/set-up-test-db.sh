#!/bin/bash

# Reset
Reset='\033[0m'       # Text Reset

# Regular Colors
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White
BRed='\033[1;31m'         # Red

TEST_DB_PATH="$(pwd)/database/test.db"
if [ -f "$TEST_DB_PATH" ] ; then
    rm "$TEST_DB_PATH"
fi

echo "$TEST_DB_PATH"
touch "$TEST_DB_PATH"
echo -e "\n${Green}Created test database...${Reset}"

sqlite3 "$TEST_DB_PATH" < "$(pwd)/database/scripts/create_database_tables.sql"

echo -e "\n${Green}Created tables. Inserting test data...${Reset}"

PASSWORD_HASH='$argon2id$v=19$m=65536,t=3,p=4$lGQxm45YoJiMzopOT61bkA$tYVNFK/TJ0Mm7qFEeSAnGXCEM9Q7gRl/yE+pfN9JoQk'

sqlite3 "$TEST_DB_PATH" "INSERT INTO ref_usertype (type) VALUES ('user')"
sqlite3 "$TEST_DB_PATH" "INSERT INTO ref_usertype (type) VALUES ('user')"
sqlite3 "$TEST_DB_PATH" "INSERT INTO ref_usertype (type) VALUES ('admin')"
sqlite3 "$TEST_DB_PATH" "INSERT INTO ref_usertype (type) VALUES ('superadmin')"
sqlite3 "$TEST_DB_PATH" "INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (1,'testadmin', '$PASSWORD_HASH', 1, julianday('now'), julianday('now'), 1, 2)"
sqlite3 "$TEST_DB_PATH" "INSERT INTO user (id, username, password, active, time_created, time_updated, updated_by, type) VALUES (2,'testuser', '$PASSWORD_HASH', 1, julianday('now'), julianday('now'), 1, 1)"

echo -e "\n${Green}Successfully inserted test data. Running test with pytest...${Reset}"
