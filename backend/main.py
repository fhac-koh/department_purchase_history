import os
from database import database
from command import command

def main():
    dbname = './Purchase_History.db'
    if not os.path.exists(dbname):
        database_controller = database(dbname)
        database_controller.db_execute('CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, tag BLOB UNIQUE, student_number STRING, student_name STRING, usage_amount INTEGER, password STRING, salt STRING)')
        database_controller.db_execute('CREATE TABLE foods(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING UNIQUE, price NUMERIC)')
        database_controller.db_execute('CREATE TABLE history(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, food_id INTEGER, datetime INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(food_id) REFERENCES foods(id))')
        database_controller.db_commit()
    cmd = command(dbname)
    while True:
        cmd.start()

if __name__ == "__main__":
    main()
