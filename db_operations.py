from datetime import datetime
import sqlite3


def connect2db(name):
    try:
        return sqlite3.connect(name)
    except:
        print(f"Problem connecting to DB {name}")
    return None


def close_db(conn):
    conn.close()
    print("sqlite connection is closed")


def create_todo_table(conn):
    try:
        sqlite_create_table_query = '''CREATE TABLE TodoList (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL UNIQUE,
                                        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    );'''

        cursor = conn.cursor()
        print("Successfully Connected to SQLite")
        cursor.execute(sqlite_create_table_query)
        conn.commit()
        print("TodoList table created")

        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)


def insert_new_task(conn, task):
    try:
        cursor = conn.cursor()
        print("Successfully Connected to SQLite")

        sqlite_insert_query = f'INSERT INTO TodoList (name) VALUES ("{task}")'
        print(sqlite_insert_query)

        count = cursor.execute(sqlite_insert_query)
        conn.commit()
        print("New Task created", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)


def get_all_tasks(conn):
    try:
        cursor = conn.cursor()
        print("Successfully Connected to SQLite")

        sqlite_select_query = f"SELECT name, creation_date FROM TodoList"

        cursor.execute(sqlite_select_query)
        tasks = cursor.fetchall()
        cursor.close()

        return tasks

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
        
    return []


if __name__ == "__main__":
    sqlite_connection = connect2db("todo_db.db")
    create_todo_table(sqlite_connection)
    close_db(sqlite_connection)
