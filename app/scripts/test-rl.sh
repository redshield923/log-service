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


echo -e "\n${Blue}Testing Rate Limiting implementation on path '/'...${Reset}"

for i in {1..20}; do echo -n "Recieved status code: ${BRed}$(curl -X 'GET' http://127.0.0.1:8000/ -o /dev/null -w '%{http_code}\n' -s)${Reset} on request ${Green} $i ${Reset} at "; date ; sleep 5; done