from typing import *
from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from os import path

from src.models import BaseModel, Movie, Link, Rating, Tag, load_from_csv

DB_PATH="./.data.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
if not path.exists(DB_PATH):
    BaseModel.metadata.create_all(engine)
    with Session(engine) as session:
        load_from_csv(session)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return {'hello': 'world'}

#########
# LOGIN #
#########

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    return jsonify({
        "message": "Login successful",
        "user": {
            "username": username,
            "userId": 1  # Placeholder user ID
        },
        "token": "placeholder_jwt_token"  # TODO: Generate real JWT token
    }), 200

##########
# MOVIES #
##########

@app.route("/movies/")
def get_movies():
    with Session(engine) as session:
        tmp = session.query(Movie).all()
        return [ {"movieId": movie.movieId, "title": movie.title, "genres": movie.genres} for movie in tmp ]

@app.route("/movies/<int:movie_id>")
def get_movie(movie_id):
    with Session(engine) as session:
        movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
        if movie is None:
            return jsonify({"error": "Movie not found"}), 404
        return jsonify({"movieId": movie.movieId, "title": movie.title, "genres": movie.genres})

@app.route("/movies/", methods=["POST"])
def create_movie():
    data = request.json
    with Session(engine) as session:
        new_movie = Movie(
            movieId=data.get("movieId"),
            title=data.get("title"),
            genres=data.get("genres")
        )
        session.add(new_movie)
        session.commit()
        return jsonify({"movieId": new_movie.movieId, "title": new_movie.title, "genres": new_movie.genres}), 201

@app.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    data = request.json
    with Session(engine) as session:
        movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
        if movie is None:
            return jsonify({"error": "Movie not found"}), 404
        
        movie.title = data.get("title", movie.title)
        movie.genres = data.get("genres", movie.genres)
        session.commit()
        return jsonify({"movieId": movie.movieId, "title": movie.title, "genres": movie.genres})

@app.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    with Session(engine) as session:
        movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
        if movie is None:
            return jsonify({"error": "Movie not found"}), 404
        
        session.delete(movie)
        session.commit()
        return jsonify({"message": "Movie deleted successfully"}), 200

#########
# LINKS #
#########

@app.route("/links/")
def get_links():
    with Session(engine) as session:
        tmp = session.query(Link).all()
        return [ {"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId} for link in tmp ]

@app.route("/links/<int:movie_id>")
def get_link(movie_id):
    with Session(engine) as session:
        link = session.query(Link).filter(Link.movieId == movie_id).first()
        if link is None:
            return jsonify({"error": "Link not found"}), 404
        return jsonify({"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId})

@app.route("/links/", methods=["POST"])
def create_link():
    data = request.json
    with Session(engine) as session:
        new_link = Link(
            movieId=data.get("movieId"),
            imdbId=data.get("imdbId"),
            tmdbId=data.get("tmdbId")
        )
        session.add(new_link)
        session.commit()
        return jsonify({"movieId": new_link.movieId, "imdbId": new_link.imdbId, "tmdbId": new_link.tmdbId}), 201

@app.route("/links/<int:movie_id>", methods=["PUT"])
def update_link(movie_id):
    data = request.json
    with Session(engine) as session:
        link = session.query(Link).filter(Link.movieId == movie_id).first()
        if link is None:
            return jsonify({"error": "Link not found"}), 404
        
        link.imdbId = data.get("imdbId", link.imdbId)
        link.tmdbId = data.get("tmdbId", link.tmdbId)
        session.commit()
        return jsonify({"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId})

@app.route("/links/<int:movie_id>", methods=["DELETE"])
def delete_link(movie_id):
    with Session(engine) as session:
        link = session.query(Link).filter(Link.movieId == movie_id).first()
        if link is None:
            return jsonify({"error": "Link not found"}), 404
        
        session.delete(link)
        session.commit()
        return jsonify({"message": "Link deleted successfully"}), 200

###########
# RATINGS #
###########

@app.route("/ratings/")
def get_ratings():
    with Session(engine) as session:
        tmp = session.query(Rating).all()
        return [ {"ratingId": rating.ratingId, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp} for rating in tmp ]

@app.route("/ratings/<int:rating_id>")
def get_rating(rating_id):
    with Session(engine) as session:
        rating = session.query(Rating).filter(Rating.ratingId == rating_id).first()
        if rating is None:
            return jsonify({"error": "Rating not found"}), 404
        return jsonify({"ratingId": rating.ratingId, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp})

@app.route("/ratings/", methods=["POST"])
def create_rating():
    data = request.json
    with Session(engine) as session:
        new_rating = Rating(
            ratingId=data.get("ratingId"),
            userId=data.get("userId"),
            movieId=data.get("movieId"),
            rating=data.get("rating"),
            timestamp=data.get("timestamp")
        )
        session.add(new_rating)
        session.commit()
        return jsonify({"ratingId": new_rating.ratingId, "userId": new_rating.userId, "movieId": new_rating.movieId, "rating": new_rating.rating, "timestamp": new_rating.timestamp}), 201

@app.route("/ratings/<int:rating_id>", methods=["PUT"])
def update_rating(rating_id):
    data = request.json
    with Session(engine) as session:
        rating = session.query(Rating).filter(Rating.ratingId == rating_id).first()
        if rating is None:
            return jsonify({"error": "Rating not found"}), 404
        
        rating.userId = data.get("userId", rating.userId)
        rating.movieId = data.get("movieId", rating.movieId)
        rating.rating = data.get("rating", rating.rating)
        rating.timestamp = data.get("timestamp", rating.timestamp)
        session.commit()
        return jsonify({"ratingId": rating.ratingId, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp})

@app.route("/ratings/<int:rating_id>", methods=["DELETE"])
def delete_rating(rating_id):
    with Session(engine) as session:
        rating = session.query(Rating).filter(Rating.ratingId == rating_id).first()
        if rating is None:
            return jsonify({"error": "Rating not found"}), 404
        
        session.delete(rating)
        session.commit()
        return jsonify({"message": "Rating deleted successfully"}), 200

########
# TAGS #
########

@app.route("/tags/")
def get_tags():
    with Session(engine) as session:
        tmp = session.query(Tag).all()
        return [ {"tagId": tag.tagId, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp} for tag in tmp ]

@app.route("/tags/<int:tag_id>")
def get_tag(tag_id):
    with Session(engine) as session:
        tag = session.query(Tag).filter(Tag.tagId == tag_id).first()
        if tag is None:
            return jsonify({"error": "Tag not found"}), 404
        return jsonify({"tagId": tag.tagId, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp})

@app.route("/tags/", methods=["POST"])
def create_tag():
    data = request.json
    with Session(engine) as session:
        new_tag = Tag(
            tagId=data.get("tagId"),
            userId=data.get("userId"),
            movieId=data.get("movieId"),
            tag=data.get("tag"),
            timestamp=data.get("timestamp")
        )
        session.add(new_tag)
        session.commit()
        return jsonify({"tagId": new_tag.tagId, "userId": new_tag.userId, "movieId": new_tag.movieId, "tag": new_tag.tag, "timestamp": new_tag.timestamp}), 201

@app.route("/tags/<int:tag_id>", methods=["PUT"])
def update_tag(tag_id):
    data = request.json
    with Session(engine) as session:
        tag = session.query(Tag).filter(Tag.tagId == tag_id).first()
        if tag is None:
            return jsonify({"error": "Tag not found"}), 404
        
        tag.userId = data.get("userId", tag.userId)
        tag.movieId = data.get("movieId", tag.movieId)
        tag.tag = data.get("tag", tag.tag)
        tag.timestamp = data.get("timestamp", tag.timestamp)
        session.commit()
        return jsonify({"tagId": tag.tagId, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp})

@app.route("/tags/<int:tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    with Session(engine) as session:
        tag = session.query(Tag).filter(Tag.tagId == tag_id).first()
        if tag is None:
            return jsonify({"error": "Tag not found"}), 404
        
        session.delete(tag)
        session.commit()
        return jsonify({"message": "Tag deleted successfully"}), 200
