#!/bin/bash
./test.sh
echo $RESULTS
pipenv run uvicorn main:app --reload --port 8000