from typing import *
from functools import wraps
from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from os import path
from datetime import datetime, timedelta
import jwt
import bcrypt
import json

from src.models import BaseModel, Movie, Link, Rating, Tag, User, load_from_csv

DB_PATH="./.data.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
if not path.exists(DB_PATH):
    BaseModel.metadata.create_all(engine)
    with Session(engine) as session:
        load_from_csv(session)

app = Flask(__name__)

SECRET_KEY = "klucz"
ALGORITHM = "HS256"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format. Use: Bearer <token>"}), 401

        if not token:
            return jsonify({"error": "Token is missing. Authorization header required"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid token format. Use: Bearer <token>"}), 401

        if not token:
            return jsonify({"error": "Token is missing. Authorization header required"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.current_user = payload

            roles = payload.get("roles", [])
            if "ROLE_ADMIN" not in roles:
                return jsonify({"error": "Access denied. ROLE_ADMIN required"}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


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

    with Session(engine) as session:
        user = session.query(User).filter(User.username == username).first()
        if user is None:
            return jsonify({"error": f"User {username} not found"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({"error": "Invalid password"}), 401

        try:
            roles = json.loads(user.roles) if user.roles else []
        except json.JSONDecodeError:
            roles = []

    payload = {
        "sub": username,
        "roles": roles,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return jsonify({
        "message": "Login successful",
        "user": {
            "username": user.username,
            "roles": roles
        },
        "access_token": token,
        "token_type": "bearer"
    }), 200


@app.route("/user_details", methods=["GET"])
@token_required
def get_user_details():
    user_payload = request.current_user
    return jsonify({
        "username": user_payload.get("sub"),
        "roles": user_payload.get("roles", []),
        "issued_at": user_payload.get("iat"),
        "expires_at": user_payload.get("exp")
    }), 200


@app.route("/users", methods=["POST"])
@admin_required
def create_user():
    data = request.json
    hashed_password = bcrypt.hashpw(
        data.get("password").encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')

    roles = data.get("roles", ["ROLE_USER"])

    with Session(engine) as session:
        new_user = User(
            username=data.get("username"),
            password=hashed_password,
            roles=json.dumps(roles)
        )
        session.add(new_user)
        session.commit()
        return jsonify({
            "username": new_user.username,
            "roles": roles
        }), 201

##########
# MOVIES #
##########

@app.route("/movies/")
@token_required
def get_movies():
    with Session(engine) as session:
        tmp = session.query(Movie).all()
        return [ {"movieId": movie.movieId, "title": movie.title, "genres": movie.genres} for movie in tmp ]

@app.route("/movies/<int:movie_id>")
@token_required
def get_movie(movie_id):
    with Session(engine) as session:
        movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
        if movie is None:
            return jsonify({"error": "Movie not found"}), 404
        return jsonify({"movieId": movie.movieId, "title": movie.title, "genres": movie.genres})

@app.route("/movies/", methods=["POST"])
@token_required
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
@token_required
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
@token_required
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
@token_required
def get_links():
    with Session(engine) as session:
        tmp = session.query(Link).all()
        return [ {"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId} for link in tmp ]

@app.route("/links/<int:movie_id>")
@token_required
def get_link(movie_id):
    with Session(engine) as session:
        link = session.query(Link).filter(Link.movieId == movie_id).first()
        if link is None:
            return jsonify({"error": "Link not found"}), 404
        return jsonify({"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId})

@app.route("/links/", methods=["POST"])
@token_required
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
@token_required
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
@token_required
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
@token_required
def get_ratings():
    with Session(engine) as session:
        tmp = session.query(Rating).all()
        return [ {"ratingId": rating.ratingId, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp} for rating in tmp ]

@app.route("/ratings/<int:rating_id>")
@token_required
def get_rating(rating_id):
    with Session(engine) as session:
        rating = session.query(Rating).filter(Rating.ratingId == rating_id).first()
        if rating is None:
            return jsonify({"error": "Rating not found"}), 404
        return jsonify({"ratingId": rating.ratingId, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp})

@app.route("/ratings/", methods=["POST"])
@token_required
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
@token_required
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
@token_required
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
@token_required
def get_tags():
    with Session(engine) as session:
        tmp = session.query(Tag).all()
        return [ {"tagId": tag.tagId, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp} for tag in tmp ]

@app.route("/tags/<int:tag_id>")
@token_required
def get_tag(tag_id):
    with Session(engine) as session:
        tag = session.query(Tag).filter(Tag.tagId == tag_id).first()
        if tag is None:
            return jsonify({"error": "Tag not found"}), 404
        return jsonify({"tagId": tag.tagId, "userId": tag.userId, "movieId": tag.movieId, "tag": tag.tag, "timestamp": tag.timestamp})

@app.route("/tags/", methods=["POST"])
@token_required
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
@token_required
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
@token_required
def delete_tag(tag_id):
    with Session(engine) as session:
        tag = session.query(Tag).filter(Tag.tagId == tag_id).first()
        if tag is None:
            return jsonify({"error": "Tag not found"}), 404

        session.delete(tag)
        session.commit()
        return jsonify({"message": "Tag deleted successfully"}), 200
