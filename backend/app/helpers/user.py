from .database import DatabaseHelper
from ..models.database import User


class UserHelper:

    databaseHelper: DatabaseHelper

    def __init__(self, databaseHelper: DatabaseHelper):
        self.databaseHelper = databaseHelper

    def create_new_users(self, username: str, password: str, updated_by: int, type: int):
        con, cur = self.databaseHelper.get_database_connection()

        create_new_users_sql = """
            INSERT INTO user
            (username, password, active, time_created,
             time_updated, updated_by, type)
            VALUES (?, ?, 1, julianday('now'), julianday('now'), ?, ?)
        """

        try:

            cur.execute(create_new_users_sql,
                        (username, password, updated_by, type,))
            con.commit()
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
            return False

        con.close()

        return True
