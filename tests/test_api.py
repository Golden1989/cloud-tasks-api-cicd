import pytest
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_health(client):
    result = client.get("/health")
    assert result.status_code == 200
    assert result.json["status"] == "ok"


def test_create_and_list(client):
    result = client.post("/tasks", json={"title": "Estudar GitHub Actions"})
    assert result.status_code == 201
    assert result.json["id"] == 1
    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json) == 1
    assert listed.json[0]["title"] == "Estudar GitHub Actions"


def test_invalid_title(client):
    assert client.post("/tasks", json={"title": "  "}).status_code == 400


def test_mark_done(client):
    item = client.post("/tasks", json={"title": "Deploy"}).json
    result = client.patch(f'/tasks/{item["id"]}', json={"done": True})
    assert result.status_code == 200
    assert client.get("/tasks").json[0]["done"] is True


def test_not_found(client):
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404


def test_delete_task(client):
    item = client.post("/tasks", json={"title": "Remover"}).json
    result = client.delete(f'/tasks/{item["id"]}')
    assert result.status_code == 204
    assert client.get("/tasks").json == []


def test_delete_not_found(client):
    assert client.delete("/tasks/999").status_code == 404


def test_filter_by_done(client):
    client.post("/tasks", json={"title": "Pendente"})
    done_item = client.post("/tasks", json={"title": "Concluida"}).json
    client.patch(f'/tasks/{done_item["id"]}', json={"done": True})

    pending = client.get("/tasks?done=false").json
    completed = client.get("/tasks?done=true").json

    assert [t["title"] for t in pending] == ["Pendente"]
    assert [t["title"] for t in completed] == ["Concluida"]


def test_filter_invalid_value(client):
    assert client.get("/tasks?done=maybe").status_code == 400
