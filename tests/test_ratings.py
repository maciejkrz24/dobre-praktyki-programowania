import pytest
from src.models import Rating


def get_auth_token(client, username, password):
    response = client.post("/login", json={"username": username, "password": password})
    data = response.get_json()
    return data.get("access_token")


def test_get_ratings_list(client, sample_ratings, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/ratings/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["userId"] == 1


def test_get_rating_by_id(client, sample_ratings, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/ratings/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["ratingId"] == 1
    assert data["userId"] == 1
    assert data["movieId"] == 1
    assert data["rating"] == 4


def test_get_rating_not_found(client, sample_ratings, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/ratings/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_create_rating(client, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    new_rating_data = {
        "ratingId": 100,
        "userId": 5,
        "movieId": 10,
        "rating": 5,
        "timestamp": 1234567890,
    }

    response = client.post(
        "/ratings/", json=new_rating_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["ratingId"] == 100
    assert data["rating"] == 5

    rating = test_session.query(Rating).filter(Rating.ratingId == 100).first()
    assert rating is not None
    assert rating.rating == 5


def test_update_rating(client, sample_ratings, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    update_data = {"rating": 5, "timestamp": 9999999999}

    response = client.put(
        "/ratings/1", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["rating"] == 5
    assert data["timestamp"] == 9999999999

    rating = test_session.query(Rating).filter(Rating.ratingId == 1).first()
    assert rating.rating == 5


def test_update_rating_not_found(client, sample_ratings, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.put(
        "/ratings/999", json={"rating": 3}, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_delete_rating(client, sample_ratings, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/ratings/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    rating = test_session.query(Rating).filter(Rating.ratingId == 1).first()
    assert rating is None


def test_delete_rating_not_found(client, sample_ratings, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete(
        "/ratings/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
