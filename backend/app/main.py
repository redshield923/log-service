from app import App
import os

server: object = App(version="0.0.1", database_path=os.environ['LOGGING_DATABASE_PATH'], secret=os.environ['LOGGING_SECRET'])

app: object = server.get_app()

