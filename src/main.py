from typing import *
from flask import Flask
from src.models import Movie, Link, Rating, Tag

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {'hello': 'world'}

@app.route("/movies/")
def get_movies():
    return [ movie.__dict__ for movie in Movie.load_movies() ]

@app.route("/links/")
def get_links():
    return [ link.__dict__ for link in Link.load_links() ]

@app.route("/ratings/")
def get_ratings():
    return [ rating.__dict__ for rating in Rating.load_ratings() ]

@app.route("/tags/")
def get_tags():
    return [ tag.__dict__ for tag in Tag.load_tags() ]