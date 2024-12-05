import sqlite3
import bcrypt
import sys

def add_user(db_path, username, password):
    """Добавляет нового пользователя в базу данных.

    Args:
        db_path (str): Путь к базе данных.
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
    """

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                           (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
            conn.commit()
    except Exception as _:
        print("Ошибка при подключении к базе данных. Попробуйте запустить основное приложение")
        print('Error connecting to database, try to start the main app. (app.py)')

if __name__ == '__main__':

    db_path = 'pqicb.db'

    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        if len(password) < 6:
            msg = (
                "Пароль должен быть не менее 6 символов.\n"
                "Используйте минимум 1 цифру, 1 Заглавную и 1 строчную букву.\n"
                "Password must be at least 6 characters.\n"
                "Use at least 1 number, 1 uppercase and 1 lowercase letter."
            )
            print(msg)
            exit(1)

        if not username or not password:
            exit(1)

        add_user(db_path, username, password)
    else:
        print("Укажите логин и пароль. Пример: py add_user.py popov 123456")
