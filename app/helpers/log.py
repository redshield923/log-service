from calendar import c
from signal import pause
import sqlite3
from typing import List

from .database import DatabaseHelper
from models.database import Index, LogResult


class LogHelper:

    databaseHelper: DatabaseHelper

    def __init__(self, databaseHelper: DatabaseHelper):
        self.databaseHelper = databaseHelper

    def ingest_log(self, index: str, source: str, payload):
        # insert a log
        # get§

        con, cur = self.databaseHelper.get_database_connection()

        create_new_log_sql = "INSERT INTO log (index_name, time_ingested, source) VALUES (?, julianday('now'), ?)"
        try:

            cur.execute(create_new_log_sql, (index, source))

        except sqlite3.IntegrityError as err:
            con.close()
            print(err)
            raise err
        log_id = cur.lastrowid
        con.commit()

        # Parse json and insert a field for each key/value pair

        for k, v in payload.items():
            create_new_field_sql = "INSERT INTO field (log_id, name, payload) VALUES (?, ?, ?)"
            cur.execute(create_new_field_sql, (log_id, k, v))
            con.commit()

        con.close()

        return len(payload.items())

    def retrieve_all_indexes(self):
        con, cur = self.databaseHelper.get_database_connection()

        cur.execute("SELECT * FROM log_index")
        res = cur.fetchall()

        con.close()

        if not res:
            return False

        index_result: List[Index] = []

        for row in res:

            formatted_row: Index = dict(row)

            index_result.append(formatted_row)

        return index_result

    def create_index(self, index_name: str, user: int):

        con, cur = self.databaseHelper.get_database_connection()

        create_index_sql = "INSERT INTO log_index VALUES ( ?, julianday('now'), julianday('now'), ?)"

        try:

            cur.execute(create_index_sql, (index_name, user,))

        except sqlite3.IntegrityError as err:
            con.close()

            print(err)
            raise err
        last_row_id = cur.lastrowid
        con.commit()

        cur.execute('SELECT * FROM log_index WHERE rowid = ?', (last_row_id,))
        inserted_row = cur.fetchone()
        con.commit()
        con.close()

        return inserted_row

    def create_if_not_exists(self, index_name: str, user_id: int):

        con, cur = self.databaseHelper.get_database_connection()

        find_index_sql = "SELECT * FROM log_index WHERE name = ?"

        cur.execute(find_index_sql, (index_name,))
        res: Index = cur.fetchone()
        print()
        print(res)
        con.close()
        if not res:
            return self.create_index(index_name, user_id)

        return False

    def retrieve_index(self, index: str):

        get_logs_from_index_sql = """
            select i.name as index_name, f.name as field, f.payload as message, l.time_ingested as timestamp, l.source as source
            from field as f
            INNER JOIN log as l on f.log_id = l.id
            inner join log_index as i on i.name = l.index_name
            where i.name = ?
            """

        con, cur = self.databaseHelper.get_database_connection()

        cur.execute(get_logs_from_index_sql, (index,))

        res = cur.fetchall()

        con.close()

        if not res:
            return False

        index_result: List[LogResult] = []

        for row in res:

            formatted_row: LogResult = dict(row)

            index_result.append(formatted_row)

        print(index_result)
        return index_result

    def retrieve_index_by_pattern(self, search: str, ):

        get_logs_from_index_pattern_sql = f"""
        select i.name as index_name, f.name as field, f.payload as message, l.time_ingested as timestamp, l.source as source
        from field as f
        INNER JOIN log as l on f.log_id = l.id
        inner join log_index as i on i.name = l.index_name
        where i.name LIKE ?
        """

        con, cur = self.databaseHelper.get_database_connection()

        cur.execute(get_logs_from_index_pattern_sql, (search,))

        res = cur.fetchall()

        con.close()

        if not res:
            return False

        index_result: List[LogResult] = []

        for row in res:

            formatted_row: LogResult = dict(row)

            index_result.append(formatted_row)

        return index_result

    def delete_index(self, index: str):

        delete_fields_sql = """
            DELETE FROM field where log_id IN (
                
                SELECT id from log where index_name = ?
                
            )
            """

        delete_logs_sql = """
            DELETE FROM log WHERE index_name = ?
        """

        delete_index_sql = """
            DELETE from log_index where name = ?
        """

        con, cur = self.databaseHelper.get_database_connection()
        cur.execute(delete_fields_sql, (index,))
        cur.execute(delete_logs_sql, (index,))
        cur.execute(delete_index_sql, (index,))
        con.commit()
        con.close()

        return True
