from typing import List

from sqlalchemy import String, create_engine, select, DateTime, ForeignKey, UniqueConstraint, desc, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from sqlalchemy.sql import func

import os
from abc import abstractmethod, ABC


class Base(DeclarativeBase):
    def to_dict(self):
        data = {}
        columns = self.__table__.columns.keys()
        for c in columns:
            data[c] = getattr(self, c)
        return data


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="user")

    def to_json(self):
        return "{}'id': {}, 'name' : '{}'{}".format('{', self.id, self.name, '}')

    def __repr__(self):
        return f"<User name: {self.name}>"


class Tweet(Base):
    __tablename__ = "tweet"
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(280))
    posted_on: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    posted_by: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="tweets")

    def __repr__(self):
        return f"<Tweet: {self.message}, Posted by: {self.user.name}, Posted on: {self.posted_on}>"

    def to_json(self):
        return {
            "tweet_id": self.id,
            "message": self.message,
            "posted_on": self.posted_on.isoformat(),
            "user_id": self.posted_by
        }


class Follower(Base):
    __tablename__ = "follower"
    id: Mapped[int] = mapped_column(primary_key=True)
    followee_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    followed_on: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UniqueConstraint("followee_id", "follower_id", name="uix_1")


class Like(Base):
    __tablename__ = "like"
    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweet.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    liked_on: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    UniqueConstraint("tweet_id", "user_id", name="uix_1")


class DbWrapper(ABC):
    def __init__(self):
        self.set_engine()
        self._session = None
        self.setup()

    @abstractmethod
    def set_engine(self):
        pass

    @abstractmethod
    def setup(self):
        pass

    @property
    def session(self):
        if self._session == None:
            self._session = Session(self._engine)
        return self._session

    def add_user(self, name: str):
        user = User(name=name)
        self.session.add(user)
        self.session.commit()

    def get_users(self, filter: str):
        stmt = select(User)
        if not filter is None:
            stmt = select(User).filter(User.name.like(f"%{filter}%"))
            print(stmt)
        result = self.session.execute(stmt).scalars().all()
        json_result = []
        for r in result:
            json_result.append(r.to_json())
        return json_result

    def get_user(self, id):
        result = self.session.get(User, id)
        if result is None:
            return "{}"
        else:
            return result.to_json()

    def add_tweet(self, message: str, user_id: int) -> str:
        # Assignment implementation
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            tweet = Tweet(message=message, posted_by=user_id)
            self.session.add(tweet)
            self.session.commit()
        else:
            return f"User with ID {user_id} does not exist"

    def get_tweets(self, filter: str):
        # Assignment 2 implementation
        stmt = select(Tweet, User.name).join(User, Tweet.posted_by == User.id)
        if filter:
            stmt = stmt.filter(Tweet.message.like(f"%{filter}%"))
        result = self.session.execute(stmt).all()
        json_result = [
            {"tweet": tweet.to_json(), "posted by": user_name}
            for tweet, user_name in result
        ]
        return json_result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def follow(self, followee, follower):

        if followee == follower:
            raise ValueError("Users cannot follow themselves.")
        existing_follow = self.session.query(Follower).filter(
            Follower.followee_id == followee,
            Follower.follower_id == follower
        ).one_or_none()

        if existing_follow:
            raise ValueError("Follow relationship already exists.")
        self.session.add(Follower(followee_id=followee, follower_id=follower))
        self.session.commit()

    def unfollow(self, followee, follower):

        relationship = self.session.query(Follower).filter(
            Follower.followee_id == followee,
            Follower.follower_id == follower
        ).one_or_none()

        if relationship:
            self.session.delete(relationship)
            self.session.commit()

    def add_like(self, tweet, user):
        if self.session.query(Like).filter_by(tweet_id=tweet, user_id=user).scalar():
            raise ValueError(f"Tweet already liked by user with ID {user}.")
        self.session.add(Like(tweet_id=tweet, user_id=user))
        self.session.commit()

    def remove_like(self, tweet, user):
        like = self.session.query(Like).filter_by(tweet_id=tweet, user_id=user).one_or_none()
        if like:
            self.session.delete(like)
            self.session.commit()

    def get_user_feed(self, user_feed):
        followed_ids_query = self.session.query(Follower.followee_id).filter(
            Follower.follower_id == user_feed
        ).subquery('followed_users')

        feed_query = (
            self.session.query(
                Tweet.message.label('tweet_text'),
                User.name.label('user_name'),
                Tweet.posted_on.label('posted_on'),
                func.count(Like.id).label('total_likes')
            )
            .join(User, Tweet.posted_by == User.id)
            .outerjoin(Like, Tweet.id == Like.tweet_id)
            .filter(Tweet.posted_by.in_(followed_ids_query))
            .group_by(Tweet.id, User.name)
            .order_by(desc(Tweet.posted_on), desc('total_likes'))
        )

        feed_items = feed_query.all()

        formatted_feed = [
            {
                "tweet": item.tweet_text,
                "posted_by": item.user_name,
                "posted_on": item.posted_on.isoformat(),
                "Num of likes": item.total_likes
            }
            for item in feed_items
        ]

        return formatted_feed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session is not None:
            self._session.close()


class SqlLiteDbWrapper(DbWrapper):

    def __init__(self, db_file_path):
        self._path = db_file_path
        super().__init__()

    def set_engine(self):
        self._engine = create_engine("sqlite:///" + self._path)

    def setup(self):
        if os.path.exists(self._path):
            return
        Base.metadata.create_all(self._engine)