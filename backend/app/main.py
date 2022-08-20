from app import App
import os

server: object = App("0.0.1", os.environ['LOGGING_DATABASE_PATH'])

app: object = server.get_app()

