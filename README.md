# log-service

This service will enable applications to post logs over HTTPs and provides basic visualisation of those logs in a tabulated form.

The basic functionality is:

- Logs posted in to the service and stored in a database.
- Ability to view all logs, given a service name or id, including filtering
- Associate log line(s) to a ticket, where the endpoint of the ticket system is provided
- Delete logs (admin users only)
- 

# Set up

This application is written in python. To install all dependecies, run:

```bash
pip install -r requirements.txt 
```

Note: if running in a virtualenv, see instructions below

# Running the application

The application can be run with 

```bash
./run.sh
```

from /app. Note you may need to:

```bash
chmod +X ./run.sh
```

on first use.


To run manually...

# Testing

Tests can be run with 

```bash
./test.sh
```

from /app. Note you may need to:

```bash
chmod +X ./test.sh
```

on first use.

# Set up

Set the following Environment Variables:

'LOGGING_DATABASE_PATH' = The full path of the sqlite3 database to connect to.
'LOGGING_SECRET' = Secret used by authentication functions. Can be generated via the following:
```bash
openssl rand -hex 32
```


Then run with 

```bash
cd backend
pipenv shell
pipenv install --deploy
pipenv run uvicorn app.main:app --reload
```

# Authentication

Authentication with JWT Tokens has been implemented. To add auth to a route, copy the following:

```python
def __route_health(current_user: User = Depends(self.get_current_user)):
    
    
    if current_user.type == 2:
        return HTTPException(status_code=403)
    
    return self.health()
```

# PipEnv Virtual Environment
To run inside of a virtual environment, run the following commands (requires python 3.8 or above ):

```bash
cd app
pipenv activate
pipenv shell

# You should now be in a virtualenv shell

./run.sh

```