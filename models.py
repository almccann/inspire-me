import sqlite3

def drop_table():
    with sqlite3.connect('users.db') as connection:
        c = connection.cursor()
        c.execute("""DROP TABLE IF EXISTS users;""")
    return True

def create_db():
    with sqlite3.connect('users.db') as connection:
        c = connection.cursor()
        table = """CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            access_token TEXT NOT NULL,
            scope TEXT NOT NULL,
            team_name TEXT NOT NULL,
            team_id TEXT NOT NULL,
            bot_user_id TEXT NOT NULL,
            bot_access_token TEXT NOT NULL
        );
        """
        c.execute(table)
    return True

if __name__ == '__main__':
    drop_table()
    create_db()
