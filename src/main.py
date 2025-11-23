from typing import *
from flask import Flask

app = Flask(__name__)

class Movie:
    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres

    def __repr__(self):
        return f"Movie({self.movieId}: '{self.title}' [{self.genres}])"

def load_movies():
    print("Opening movies.csv...")
    with open('./movies/movies.csv', 'r') as f:
        for (idx, line) in enumerate(f.readlines()):
            if idx == 0: continue
            movie = line.strip().split(',')
            movieId = movie[0]
            title = movie[1]
            genres = movie[2]
            yield Movie(movieId, title, genres)

@app.route("/")
def hello_world():
    return {'hello': 'world'}

@app.route("/movies/")
def get_movies():
    movies = [ movie.__dict__ for movie in load_movies() ]
    return movies