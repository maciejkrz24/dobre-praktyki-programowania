import pytest
from src.models import Movie


def get_auth_token(client, username, password):
    response = client.post("/login", json={"username": username, "password": password})
    data = response.get_json()
    return data.get("access_token")


def test_get_movies_list(client, sample_movies, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/movies/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["title"] == "Toy Story (1995)"


def test_get_movie_by_id(client, sample_movies, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/movies/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["movieId"] == 1
    assert data["title"] == "Toy Story (1995)"
    assert "Adventure" in data["genres"]


def test_get_movie_not_found(client, sample_movies, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/movies/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_create_movie(client, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    new_movie_data = {
        "movieId": 100,
        "title": "Test Movie (2024)",
        "genres": "Action|Thriller",
    }

    response = client.post(
        "/movies/", json=new_movie_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["movieId"] == 100
    assert data["title"] == "Test Movie (2024)"

    movie = test_session.query(Movie).filter(Movie.movieId == 100).first()
    assert movie is not None
    assert movie.title == "Test Movie (2024)"


def test_update_movie(client, sample_movies, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    update_data = {"title": "Updated Toy Story (1995)", "genres": "Animation|Comedy"}

    response = client.put(
        "/movies/1", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Toy Story (1995)"
    assert data["genres"] == "Animation|Comedy"

    movie = test_session.query(Movie).filter(Movie.movieId == 1).first()
    assert movie.title == "Updated Toy Story (1995)"


def test_update_movie_not_found(client, sample_movies, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.put(
        "/movies/999",
        json={"title": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_delete_movie(client, sample_movies, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/movies/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    movie = test_session.query(Movie).filter(Movie.movieId == 1).first()
    assert movie is None


def test_delete_movie_not_found(client, sample_movies, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete(
        "/movies/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
