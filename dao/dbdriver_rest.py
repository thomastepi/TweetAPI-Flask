from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os


Base = declarative_base()

DB_FILE_PATH = 'app_1.db'


class Books(Base):
    __tablename__ = "books"
    bookId = Column(BigInteger, primary_key=True)
    title = Column(String)
    author = Column(String)

    def __str__(self):
        return f"book title: {self.title};\nauthor:{self.author};"

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
    # db.setup()
    session = db.get_session()
    # new_book = Books()
    # new_book.bookId = 1
    # new_book.title = "Some book"
    # new_book.author = "Unknown"

    # session.add(new_book)

    session.flush()
    session.commit()

    books = session.query(Books)
    for b in books:
        print(b)
