# pylint: disable=E0402,E0401,E0611

import sqlite3
from .database import DatabaseHelper


class UserHelper:

    databaseHelper: DatabaseHelper

    def __init__(self, database_helper: DatabaseHelper):

        # pylint: disable=C0103
        self.databaseHelper = database_helper

    def create_new_user(self, username: str, password: str, updated_by: int, user_type: int):
        con, cur = self.databaseHelper.get_database_connection()

        create_new_user_sql = """
            INSERT INTO user
            (username, password, active, time_created,
             time_updated, updated_by, type)
            VALUES (?, ?, 1, julianday('now'), julianday('now'), ?, ?)
        """

        try:

            res = cur.execute(create_new_user_sql,
                              (username, password, updated_by, user_type,))

            con.commit()
            print(res.rowcount)
        except sqlite3.Error as err:
            print(err)
            con.close()
            return False

        con.close()
        return True

    def update_password(self, username: str, password: str):

        con, cur = self.databaseHelper.get_database_connection()

        update_user_password_sql = """
            UPDATE user SET password = ? WHERE username = ?
        """

        try:

            cur.execute(update_user_password_sql,
                        (password, username,))
            con.commit()
        except sqlite3.Error as err:
            print(err)
            con.close()
            return False

        con.close()
        return True

    def delete_user(self, username: str):

        con, cur = self.databaseHelper.get_database_connection()

        delete_user_password_sql = """
            DELETE FROM user WHERE username = ?
        """

        try:

            cur.execute(delete_user_password_sql,
                        (username,))
            con.commit()
        except sqlite3.Error as err:
            print(err)
            con.close()
            return False

        con.close()
        return True
