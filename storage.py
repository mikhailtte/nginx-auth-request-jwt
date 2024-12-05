
import os
import sqlite3
from contextlib import contextmanager
import bcrypt
from flask import Flask
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, field_validator

config_path = '.config.env'

class Db:
    DATABASE = 'pqicb.db'

    def __init__(self):
        self._conn = None

    @contextmanager
    def get_connection(self):
        if not self._conn:
            self._conn = sqlite3.connect(self.DATABASE)
        try:
            yield self._conn
        finally:
            if self._conn:
                self._conn.commit()
                self._conn.close()
                self._conn = None

    def init_db(self, app: Flask):
        with self.get_connection() as conn:
            with app.open_resource('schema.sql', mode='r') as f:
                conn.cursor().executescript(f.read())

    def query_db(self, query, args=()): # <======================================
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, args)
            rv = cur.fetchall()
            return rv

    def add_user(self, username, password): # <======================================
        with self.get_connection() as conn:
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            conn.execute(query, (username, password))
        return True

    def check_credentials(self, username: str, password: str): # <======================================
        try:
            user = self.query_db('SELECT * FROM users WHERE username=?', (username,))
            if user:
                hashed_password = user[0][2]
                return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            return False
        except Exception as e:
            print(f"Ошибка при проверке учетных данных: {e}")
            return False


class Config():
    @staticmethod
    def init_config(config_path):
        if not os.path.exists(config_path):
            try:
                Config.create_config_file(config_path)
                Config.notice_window(
                    f'Something is wrong! Check the configuration file! ({config_path})'
                )
            except Exception as e:
                print(f"Ошибка при создании конфигурации: {e}")
    
    @staticmethod
    def create_config_file(config_path):
        config = (
            '# Main token expiration time'
            'TOKEN_EXPIRATION_SECS = 3600'
            '# Refresh token expiration time'
            'REFRESH_TOKEN_EXP = 259200'
            '# Only HTTPS'
            'SECURE=True'
            '# hashing algorithm'
            'ALGORITHM=\'RS256\''
            'PORT = 8001'
            'HOST = \'0.0.0.0\''
            'PROTECT_PATH=\'InfoBase\''
        )

        try:
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(config)
        except IOError as e:
            print(f"Ошибка записи в файл: {e}")
        except Exception as e:
            print(f"Ошибка при создании конфигурации: {e}")

    @staticmethod
    def notice_window(message, title="Authentication Service"):
        import wx
        app = wx.App()
        dlg = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        app.MainLoop()
        exit()

class SettingsModel(BaseSettings):
        TOKEN_EXPIRATION_SECS: int = 3600
        REFRESH_TOKEN_EXP: int = 259200
        SECURE: bool = True
        ALGORITHM: str = 'RS256'
        PORT: int = 8001
        HOST: str = '127.0.0.1'
        PROTECT_PATH: str

        model_config = SettingsConfigDict(
            env_file=config_path
        )

class CredentialsModel(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Invalid Form')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 50:
            raise ValueError('Invalid Form')
        return v

Config.init_config(config_path)
db = Db()
try:
    settings = SettingsModel()
except Exception as e:
    print(f'Ошибка при чтении конфигурации: {e}')
    exit()
