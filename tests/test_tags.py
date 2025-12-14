import pytest
from src.models import Tag


def get_auth_token(client, username, password):
    response = client.post("/login", json={"username": username, "password": password})
    data = response.get_json()
    return data.get("access_token")


def test_get_tags_list(client, sample_tags, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/tags/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["tag"] == "funny"


def test_get_tag_by_id(client, sample_tags, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/tags/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["tagId"] == 1
    assert data["userId"] == 2
    assert data["tag"] == "funny"


def test_get_tag_not_found(client, sample_tags, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.get("/tags/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_create_tag(client, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    new_tag_data = {
        "tagId": 100,
        "userId": 10,
        "movieId": 50,
        "tag": "awesome",
        "timestamp": 1234567890,
    }

    response = client.post(
        "/tags/", json=new_tag_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["tagId"] == 100
    assert data["tag"] == "awesome"

    tag = test_session.query(Tag).filter(Tag.tagId == 100).first()
    assert tag is not None
    assert tag.tag == "awesome"


def test_update_tag(client, sample_tags, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    update_data = {"tag": "hilarious", "timestamp": 9999999999}

    response = client.put(
        "/tags/1", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["tag"] == "hilarious"
    assert data["timestamp"] == 9999999999

    tag = test_session.query(Tag).filter(Tag.tagId == 1).first()
    assert tag.tag == "hilarious"


def test_update_tag_not_found(client, sample_tags, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.put(
        "/tags/999", json={"tag": "test"}, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_delete_tag(client, sample_tags, test_session, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/tags/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    tag = test_session.query(Tag).filter(Tag.tagId == 1).first()
    assert tag is None


def test_delete_tag_not_found(client, sample_tags, sample_users):
    token = get_auth_token(client, "testuser_auth", "password123")
    response = client.delete("/tags/999", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
