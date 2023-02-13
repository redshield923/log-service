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

echo -e "\n${Blue}Starting docker build of ${Purple}log-service${Blue}...${Reset}"
docker build -f Dockerfile -t log-service:0.0.1 .
docker tag log-service:0.0.1 log-service:latest 
docker run --rm -d --name log-service -p 80:80 log-service:latest

if [ $? -ne 0 ]; then
    echo "${Red}Failed to build or run Docker container. Is docker installed and running?${Reset}"
    exit 1
fi

echo -e "\n${Blue}log-service${Green} running! Check out ${BRed}https://0.0.0.0:80/docs ${Green} to get started.${Reset}"
