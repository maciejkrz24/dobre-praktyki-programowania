from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class BaseModel(DeclarativeBase):
    def load():
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
