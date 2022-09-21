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

echo -e "\n${Blue}Starting local build of ${Purple}log-service ${Blue}...${Reset}"

pytho3 -m pip install --no-cache-dir --upgrade -r requirements.txt

echo -e "\n${Green}Finished local build of ${Blue}log-service${Green}.${Reset}"
pipenv run uvicorn main:app --reload --port 8000