from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_root_endpoint(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}


def test_create_user(client: TestClient, db: Session) -> None:
    data = {"email": "user@example.com", "password": "string"}

    r = client.post("/users", json=data)

    assert r.status_code == 200
