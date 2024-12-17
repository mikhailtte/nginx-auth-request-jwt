from contextlib import contextmanager
import os
from bcrypt import checkpw
from sqlalchemy import MetaData, String, select
from sqlalchemy.orm import (
    DeclarativeBase, sessionmaker, Mapped, mapped_column
)
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, field_validator

config_path = '.config.env'

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.username!r}, hash={self.password!r})"

class Database:

    # engine = create_engine("sqlite://", echo=True)
    DATABASE = 'pqicb.db'
    config_path = '.config.env'

    def __init__(self, database_uri, Base: DeclarativeBase):
        self.DATABASE_URI = database_uri
        self.engine = create_engine(self.DATABASE_URI)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Base = Base
        self.Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        session = self.session_factory()
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(e)
        finally:
            session.close()
    
    def add_user(self, username: str, password: str) -> bool:
        with self.get_session() as session:
            new_user = User()
            new_user.username = username
            new_user.password = password
            try:
                session.add(new_user)
                session.commit()
                return True
            except SQLAlchemyError as _:
                session.rollback()
                return False

    def get_user(self, name: str) -> User:
        with self.get_session() as session:
            stmt = select(User).where(User.username == name)
            user = session.execute(stmt).scalar_one()
            return user

    def check_credentials(self, username: str, password: str):
        try:
            user = self.get_user(username)
            if not user:
                return False
            elif user:
                return checkpw(password.encode('utf-8'), user.password)
        except Exception:
            return False
    
    def clean_db(self):
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        for table in reversed(metadata.sorted_tables):
            with self.get_session() as session:
                session.execute(table.delete())

class Config():
    @staticmethod
    def init_config(config_path):
        if not os.path.exists(config_path):
            try:
                Config.create_config_file(config_path)
            except IOError as e:
                print(f"Error writing to file: {e}")
            except Exception as e:
                print(f"Error creating configuration file: {e}")
    
    @staticmethod
    def create_config_file(config_path):
        config = (
            '# Token expiration date\n '
            'TOKEN_EXPIRATION_SECS = 3600\n '
            '# Refresh token expiration time\n '
            'REFRESH_TOKEN_EXP = 259200\n '
            '# HTTPS Only\n '
            'SECURE=True\n '
            '# Encryption algorithm\n '
            'ALGORITHM=\'RS256\'\n '
            'PORT = 8000\n '
            'HOST = \'0.0.0.0\'\n '
        )
        with open(config_path, 'w', encoding='utf-8') as file:
            file.write(config)

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

try:
    Config.init_config(config_path)
    settings = SettingsModel()
except Exception as e:
    print(f'Error reading configuration: {e}')
    exit()

try:
    base = Base()
    db = Database(
        f'sqlite:///{Database.DATABASE}',
        Base=base
    )
except Exception as e:
    print(f'Database connection error: {e}')
    exit()


