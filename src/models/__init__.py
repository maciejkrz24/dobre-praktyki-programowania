from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class BaseModel(DeclarativeBase):
    def load(session):
        pass

class Movie(BaseModel):
    __tablename__ = "movies"
    movieId: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    genres: Mapped[str]


class Link(BaseModel):
    __tablename__ = "links"
    movieId: Mapped[int] = mapped_column(primary_key=True)
    imdbId: Mapped[str]
    tmdbId: Mapped[str]


class Rating(BaseModel):
    __tablename__ = "ratings"
    ratingId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int]
    movieId: Mapped[int]
    rating: Mapped[int]
    timestamp: Mapped[int]


class Tag(BaseModel):
    __tablename__ = "tags"
    tagId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int]
    movieId: Mapped[int]
    tag: Mapped[str]
    timestamp: Mapped[int]


class User(BaseModel):
    __tablename__ = "users"
    userId: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]


def load_from_csv(session):
    with open("movies/movies.csv", 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if idx == 0: continue
            vals = line.strip().split(",")
            session.add(Movie(
                movieId=vals[0],
                title=vals[1],
                genres=vals[2]
            ))
    with open("movies/links.csv", 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if idx == 0: continue
            vals = line.strip().split(",")
            session.add(Link(
                movieId=vals[0],
                imdbId=vals[1],
                tmdbId=vals[2]
            ))
    with open("movies/ratings.csv", 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if idx == 0: continue
            vals = line.strip().split(",")
            session.add(Rating(
                userId=vals[0],
                movieId=vals[1],
                rating=vals[2],
                timestamp=vals[3],
            ))
    with open("movies/tags.csv", 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if idx == 0: continue
            vals = line.strip().split(",")
            session.add(Tag(
                userId=vals[0],
                movieId=vals[1],
                tag=vals[2],
                timestamp=vals[3],
            ))
    session.commit()