import sqlite3


def test():
    return True

def get_index_id(cur: sqlite3.Cursor, index: str):
    
    find_index_sql = 'SELECT * FROM log_index WHERE name = ?'
    
    cur.execute(find_index_sql, [index])
    res = cur.fetchall()
        
    
    