from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


Base = declarative_base()

DB_FILE_PATH = 'app.db'

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    pwd = Column(String)
    email = Column(String)
    dob = Column(String)

    def __str__(self):
        return f"name: {self.name};\nemail:{self.email};\ndob:{self.dob}"

class Tweet(Base):
    __tablename__ = "tweets"
    tweet_id = Column(BigInteger, primary_key=True)
    message = Column(String)
    user_id = Column(String)
    ts = Column(BigInteger)

class Follower(Base):
    __tablename__ = "followers"
    followee_id = Column(String, primary_key=True)
    follower_id = Column(String, primary_key=True)

class Like(Base):
    __tablename__ = "likes"
    tweet_id = Column(String, primary_key=True)
    user_id = Column(String, primary_key=True)

class View(Base):
    __tablename__ = "views"
    tweet_id = Column(String, primary_key=True)
    user_id = Column(String, primary_key=True)
    ts = Column(BigInteger)

class DBWrapper:
    def __init__(self):
        self._engine = None
        self._session = None
    def create_engine(self):
        if self._engine == None:
            self._engine = create_engine("sqlite:///" + DB_FILE_PATH)
        return self._engine
    def __create_all__(self):
        Base.metadata.create_all(self.create_engine())

    def __drop_all__(self):
        Base.metadata.drop_all(self.create_engine())

    def get_session(self):
        if self._session == None:
            Session = sessionmaker(bind=self.create_engine())
            self._session = Session()
            self._session.autocommit = False

        return self._session

    def close_session(self):
        if self._session == None:
            return
        self._session.close()
        self._session = None

    def setup(self, force_rebuild=False):
        if os.path.exists(DB_FILE_PATH):
            if force_rebuild:
                self.__drop_all__()
            else:
                return
        self.__create_all__()

if __name__ == "__main__":
    db = DBWrapper()
    db.setup(True)
    session = db.get_session()

    # add users
    user1 = User()
    user1.user_id = 1
    user1.name = "Andrey"
    user1.email = "and@gmail.net"
    user1.dob = "1/1/2000"
    user1.pwd = "1234"

    session.add(user1)

    user1 = User()
    user1.user_id = 2
    user1.name = "Sam"
    user1.email = "sam@gmail.net"
    user1.dob = "1/1/2000"
    user1.pwd = "1234"

    session.add(user1)

    user1 = User()
    user1.user_id = 3
    user1.name = "Frodo"
    user1.email = "frd@gmail.net"
    user1.dob = "1/1/2000"
    user1.pwd = "1234"

    session.add(user1)

    session.flush()
    session.commit()