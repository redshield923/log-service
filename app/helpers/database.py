# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115, R0903

import sqlite3


class DatabaseHelper:

    database_path: str

    def __init__(self, database_path: str):
        self.database_path = database_path

    def get_database_connection(self):
        con = sqlite3.connect(self.database_path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        return con, cur
