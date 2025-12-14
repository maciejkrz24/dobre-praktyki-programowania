import pytest
import bcrypt
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import BaseModel, Movie, Link, Rating, Tag, User
from src.main import app


@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    BaseModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    session = Session(test_engine)
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(test_engine):
    app.config["TESTING"] = True

    import src.main as main_module

    original_engine = main_module.engine
    main_module.engine = test_engine

    with app.test_client() as client:
        yield client

    main_module.engine = original_engine


@pytest.fixture(scope="function")
def sample_users(test_session):
    hashed_password = bcrypt.hashpw(
        "password123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    admin_hashed_password = bcrypt.hashpw(
        "adminpass".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    users = [
        User(
            username="testuser_auth",
            password=hashed_password,
            roles=json.dumps(["ROLE_USER"]),
        ),
        User(
            username="admin",
            password=admin_hashed_password,
            roles=json.dumps(["ROLE_ADMIN", "ROLE_USER"]),
        ),
    ]
    for user in users:
        test_session.add(user)
    test_session.commit()
    return users


@pytest.fixture(scope="function")
def sample_movies(test_session):
    movies = [
        Movie(
            movieId=1,
            title="Toy Story (1995)",
            genres="Adventure|Animation|Children|Comedy|Fantasy",
        ),
        Movie(movieId=2, title="Jumanji (1995)", genres="Adventure|Children|Fantasy"),
        Movie(movieId=3, title="Grumpier Old Men (1995)", genres="Comedy|Romance"),
    ]
    for movie in movies:
        test_session.add(movie)
    test_session.commit()
    return movies


@pytest.fixture(scope="function")
def sample_links(test_session):
    links = [
        Link(movieId=1, imdbId="0114709", tmdbId="862"),
        Link(movieId=2, imdbId="0113497", tmdbId="8844"),
        Link(movieId=3, imdbId="0113228", tmdbId="15602"),
    ]
    for link in links:
        test_session.add(link)
    test_session.commit()
    return links


@pytest.fixture(scope="function")
def sample_ratings(test_session):
    ratings = [
        Rating(ratingId=1, userId=1, movieId=1, rating=4, timestamp=964982703),
        Rating(ratingId=2, userId=1, movieId=3, rating=4, timestamp=964981247),
        Rating(ratingId=3, userId=2, movieId=1, rating=5, timestamp=964982224),
    ]
    for rating in ratings:
        test_session.add(rating)
    test_session.commit()
    return ratings


@pytest.fixture(scope="function")
def sample_tags(test_session):
    tags = [
        Tag(tagId=1, userId=2, movieId=60756, tag="funny", timestamp=1445714994),
        Tag(
            tagId=2,
            userId=2,
            movieId=60756,
            tag="Highly quotable",
            timestamp=1445714996,
        ),
        Tag(tagId=3, userId=3, movieId=89774, tag="boxing story", timestamp=1389267563),
    ]
    for tag in tags:
        test_session.add(tag)
    test_session.commit()
    return tags
