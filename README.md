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