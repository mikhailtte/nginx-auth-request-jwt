import sqlite3
import bcrypt
import sys

def add_user(db_path, username, password):

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (
                    username,
                    bcrypt.hashpw(password.encode('utf-8'),
                    bcrypt.gensalt())
                )
            )
            conn.commit()
    except Exception as e:
        print(f'Error connecting to database, try to start the main app. (app.py): {e}')

def del_user(db_path, username):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username=?', (username,))
            conn.commit()
    except Exception as e:
        print(f"Error deleting user: {e}")
        exit(1)

if __name__ == '__main__':

    db_path = 'base.db'
    flag = sys.argv[1]
    if flag == '-n':
        username = sys.argv[2]
        password = sys.argv[3]
        if len(password) < 6:
            msg = (
                "Password must be at least 6 characters.\n"
                "Use at least 1 number, 1 uppercase and 1 lowercase letter."
            )
            print(msg)
            exit()
        elif not username or not password:
            exit()
        add_user(db_path, username, password)
        print(f"User {sys.argv[2]} added")
        exit()

    if flag == '-d':
        username = sys.argv[2]
        del_user(db_path, username)
        print(f"User {sys.argv[2]} deleted")
        exit()
    
    if flag == '-l':
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users')
                rows = cursor.fetchall()
                print("ID\tUsername")
                for row in rows:
                    print(f"{row[0]}\t{row[1]}")
        except Exception as e:
            print(f"Error reading user list: {e}")
        exit()
    
    help = (
        'ADD NEW USER  add_user.py -n NAME PASS \n'
        'DELETE USER   add_user.py -d NAME \n'
        'USER LIST     add_user.py -l'
    )
    print(help)
    exit()
