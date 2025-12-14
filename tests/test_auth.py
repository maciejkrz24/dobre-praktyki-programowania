import pytest
import json
import bcrypt
import jwt as pyjwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models import User
from src.main import SECRET_KEY, ALGORITHM


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


def get_auth_token(client, username, password):
    response = client.post("/login", json={"username": username, "password": password})
    data = response.get_json()
    return data.get("access_token")


class TestLogin:
    def test_login_success(self, client, sample_users):
        response = client.post(
            "/login", json={"username": "testuser_auth", "password": "password123"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser_auth"
        assert "ROLE_USER" in data["user"]["roles"]

    def test_login_admin_success(self, client, sample_users):
        response = client.post(
            "/login", json={"username": "admin", "password": "adminpass"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "ROLE_ADMIN" in data["user"]["roles"]

    def test_login_wrong_password(self, client, sample_users):
        response = client.post(
            "/login", json={"username": "testuser_auth", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Invalid password"

    def test_login_nonexistent_user(self, client, sample_users):
        response = client.post(
            "/login", json={"username": "nonexistent", "password": "password123"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "not found" in data["error"]

    def test_login_missing_username(self, client, sample_users):
        response = client.post("/login", json={"password": "password123"})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_login_missing_password(self, client, sample_users):
        response = client.post("/login", json={"username": "testuser_auth"})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_login_empty_body(self, client, sample_users):
        response = client.post("/login", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data


class TestUsers:
    def test_create_user_as_admin(self, client, sample_users):
        token = get_auth_token(client, "admin", "adminpass")

        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "password": "newpassword123",
                "roles": ["ROLE_USER"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["username"] == "newuser"
        assert "ROLE_USER" in data["roles"]

    def test_create_user_as_admin_with_admin_role(self, client, sample_users):
        token = get_auth_token(client, "admin", "adminpass")

        response = client.post(
            "/users",
            json={
                "username": "newadmin",
                "password": "adminpass123",
                "roles": ["ROLE_ADMIN", "ROLE_USER"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "ROLE_ADMIN" in data["roles"]

    def test_create_user_without_admin_role(self, client, sample_users):
        token = get_auth_token(client, "testuser_auth", "password123")

        response = client.post(
            "/users",
            json={
                "username": "anotheruser",
                "password": "password123",
                "roles": ["ROLE_USER"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        data = response.get_json()
        assert "error" in data
        assert "ROLE_ADMIN required" in data["error"]

    def test_create_user_without_token(self, client, sample_users):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "password": "password123",
                "roles": ["ROLE_USER"],
            },
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "Token is missing" in data["error"]

    def test_create_user_with_invalid_token(self, client, sample_users):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "password": "password123",
                "roles": ["ROLE_USER"],
            },
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "Invalid token" in data["error"]

    def test_create_user_with_malformed_auth_header(self, client, sample_users):
        response = client.post(
            "/users",
            json={"username": "newuser", "password": "password123"},
            headers={"Authorization": "InvalidFormat"},
        )

        assert response.status_code == 401


class TestUserDetails:
    def test_get_user_details_success(self, client, sample_users):
        token = get_auth_token(client, "testuser_auth", "password123")

        response = client.get(
            "/user_details", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "testuser_auth"
        assert "ROLE_USER" in data["roles"]
        assert "issued_at" in data
        assert "expires_at" in data

    def test_get_user_details_admin(self, client, sample_users):
        token = get_auth_token(client, "admin", "adminpass")

        response = client.get(
            "/user_details", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "admin"
        assert "ROLE_ADMIN" in data["roles"]

    def test_get_user_details_without_token(self, client, sample_users):
        response = client.get("/user_details")

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "Token is missing" in data["error"]

    def test_get_user_details_with_invalid_token(self, client, sample_users):
        response = client.get(
            "/user_details", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "Invalid token" in data["error"]

    def test_get_user_details_with_malformed_header(self, client, sample_users):
        response = client.get(
            "/user_details", headers={"Authorization": "NoBearer token"}
        )

        assert response.status_code == 401


class TestAuthIntegration:
    def test_full_auth_flow(self, client, sample_users):
        login_response = client.post(
            "/login", json={"username": "testuser_auth", "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.get_json()["access_token"]

        details_response = client.get(
            "/user_details", headers={"Authorization": f"Bearer {token}"}
        )
        assert details_response.status_code == 200
        assert details_response.get_json()["username"] == "testuser_auth"

    def test_admin_creates_user_and_new_user_logs_in(self, client, sample_users):
        admin_token = get_auth_token(client, "admin", "adminpass")

        create_response = client.post(
            "/users",
            json={
                "username": "brandnewuser",
                "password": "brandnewpass",
                "roles": ["ROLE_USER"],
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_response.status_code == 201

        login_response = client.post(
            "/login", json={"username": "brandnewuser", "password": "brandnewpass"}
        )
        assert login_response.status_code == 200

        new_user_token = login_response.get_json()["access_token"]
        details_response = client.get(
            "/user_details", headers={"Authorization": f"Bearer {new_user_token}"}
        )
        assert details_response.status_code == 200
        assert details_response.get_json()["username"] == "brandnewuser"

    def test_protected_endpoint_requires_auth(self, client, sample_users):
        response = client.get("/movies/")
        assert response.status_code == 401

        token = get_auth_token(client, "testuser_auth", "password123")
        response = client.get("/movies/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
