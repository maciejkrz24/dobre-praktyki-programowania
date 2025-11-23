import pytest
from src.models import Movie

def test_get_movies_list(client, sample_movies):
    response = client.get("/movies/")
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["title"] == "Toy Story (1995)"

def test_get_movie_by_id(client, sample_movies):
    response = client.get("/movies/1")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["movieId"] == 1
    assert data["title"] == "Toy Story (1995)"
    assert "Adventure" in data["genres"]

def test_get_movie_not_found(client, sample_movies):
    response = client.get("/movies/999")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_create_movie(client, test_session):
    new_movie_data = {
        "movieId": 100,
        "title": "Test Movie (2024)",
        "genres": "Action|Thriller"
    }
    
    response = client.post("/movies/", json=new_movie_data)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["movieId"] == 100
    assert data["title"] == "Test Movie (2024)"
    
    movie = test_session.query(Movie).filter(Movie.movieId == 100).first()
    assert movie is not None
    assert movie.title == "Test Movie (2024)"

def test_update_movie(client, sample_movies, test_session):
    update_data = {
        "title": "Updated Toy Story (1995)",
        "genres": "Animation|Comedy"
    }
    
    response = client.put("/movies/1", json=update_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Toy Story (1995)"
    assert data["genres"] == "Animation|Comedy"
    
    movie = test_session.query(Movie).filter(Movie.movieId == 1).first()
    assert movie.title == "Updated Toy Story (1995)"

def test_update_movie_not_found(client, sample_movies):
    response = client.put("/movies/999", json={"title": "Test"})
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_delete_movie(client, sample_movies, test_session):
    response = client.delete("/movies/1")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    
    movie = test_session.query(Movie).filter(Movie.movieId == 1).first()
    assert movie is None

def test_delete_movie_not_found(client, sample_movies):
    response = client.delete("/movies/999")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
