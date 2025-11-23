from typing import *
from flask import Flask
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from os import path

from src.models import BaseModel, Movie, Link, Rating, Tag, load_from_csv

engine = create_engine("sqlite:///./.data.db", echo=True)
if not path.exists(".data.db"):
    BaseModel.metadata.create_all(engine)
    with Session(engine) as session:
        load_from_csv(session)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {'hello': 'world'}

@app.route("/movies/")
def get_movies():
    with Session(engine) as session:
        tmp = session.query(Movie).all()
        return [ {"movieId": movie.movieId, "title": movie.title, "genres": movie.genres} for movie in tmp ]

@app.route("/links/")
def get_links():
    with Session(engine) as session:
        tmp = session.query(Link).all()
        return [ {"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId} for link in tmp ]

@app.route("/ratings/")
def get_ratings():
    with Session(engine) as session:
        tmp = session.query(Rating).all()
        return [ {"userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp} for rating in tmp ]

@app.route("/tags/")
def get_tags():
    with Session(engine) as session:
        tmp = session.query(Tag).all()
        return [ {"userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp} for tag in tmp ]