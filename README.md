# log-service

This service will enable applications to post logs over HTTPs and provides basic visualisation of those logs in a tabulated form.

The basic functionality is:

- Logs posted in to the service and stored in a database.
- Ability to view all logs, given a service name or id, including filtering
- Associate log line(s) to a ticket, where the endpoint of the ticket system is provided
- Delete logs (admin users only)
- 


# Set up

Set the following Environment Variables:

'LOGGING_DATABASE_PATH' = The full path of the sqlite3 database to connect to.
'LOGGING_SECRET' = Secret used by authentication functions. Can be generated via the following:
```bash
openssl rand -hex 32
```

# Running the application

The application is split into two parts, the frontend and backend. These are both FastApi projects.

The run the backend: 

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