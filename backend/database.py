import sqlite3

class database:
    def __init__(self, dbname) -> None:
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()

    def db_execute(self, exec_sql, *args):
        return self.cur.execute(exec_sql, args)

    def db_execute_many(self, exec_sql, data):
        return self.conn.executemany(exec_sql, data)

    def db_commit(self):
        self.conn.commit()

    def db_close(self):
        self.cur.close()
        self.conn.close()
