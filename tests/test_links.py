import pytest
from src.models import Link


def get_auth_token(client, username, password):
    response = client.post("/login", json={"username": username, "password": password})
    data = response.get_json()
    return data.get("access_token")


def test_get_links_list(client, sample_links, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/links/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["imdbId"] == "0114709"


def test_get_link_by_id(client, sample_links, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/links/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["movieId"] == 1
    assert data["imdbId"] == "0114709"
    assert data["tmdbId"] == "862"


def test_get_link_not_found(client, sample_links, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/links/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_create_link(client, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    new_link_data = {"movieId": 100, "imdbId": "0123456", "tmdbId": "99999"}

    response = client.post(
        "/links/", json=new_link_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["movieId"] == 100
    assert data["imdbId"] == "0123456"

    link = test_session.query(Link).filter(Link.movieId == 100).first()
    assert link is not None
    assert link.imdbId == "0123456"


def test_update_link(client, sample_links, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    update_data = {"imdbId": "9999999", "tmdbId": "88888"}

    response = client.put(
        "/links/1", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["imdbId"] == "9999999"
    assert data["tmdbId"] == "88888"

    link = test_session.query(Link).filter(Link.movieId == 1).first()
    assert link.imdbId == "9999999"


def test_update_link_not_found(client, sample_links, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.put(
        "/links/999",
        json={"imdbId": "123"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_delete_link(client, sample_links, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/links/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    link = test_session.query(Link).filter(Link.movieId == 1).first()
    assert link is None


def test_delete_link_not_found(client, sample_links, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/links/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
