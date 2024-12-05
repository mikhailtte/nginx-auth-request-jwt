from contextlib import contextmanager
from bcrypt import checkpw
from sqlalchemy import String, select
from sqlalchemy.orm import (
    DeclarativeBase, sessionmaker, Mapped, mapped_column
)
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
Base = DeclarativeBase()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.username!r}, hash={self.password!r})"

class Database:

    engine = create_engine("sqlite://", echo=True)
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
            new_user = User(username, password)
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
        
