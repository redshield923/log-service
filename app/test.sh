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

echo -e "\n${Blue}Setting up local test environment...${Reset}"

python3 -m pip install pytest
if [ ! $? -eq 0 ]; then
    echo "${Red}Pip install failed. Do you have Python3 installed?${Reset}"
    exit 1
fi

source ./scripts/set-up-test-db.sh || exit 1

LOGGING_DATABASE_PATH=$TEST_DB_PATH LOGGING_SECRET=$(openssl rand -hex 32) pytest "$(pwd)/test.py"

echo -e "\n${Green}Testing finished. Clearing up..${Reset}"

rm "$TEST_DB_PATH"

echo -e "\n${Green}Successfully cleared up. Exiting${Reset}"
