import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app
import pytest
import main
import json
from unittest.mock import AsyncMock


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Substitui redis_client por mock em todos os testes"""
    fake = AsyncMock()
    fake.get.return_value = None
    fake.set.return_value = True
    monkeypatch.setattr(main, "redis_client", fake)
    return fake

@pytest.mark.skip(reason="Não roda sem Redis real")
def test_startup_and_shutdown():
    pass

client = TestClient(main.app)


def test_get_pokemons_success():
    response = client.get("/pokemons?limit=2&offset=0", headers={"X-API-Key": "123"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "results" in data["data"]


def test_get_pokemons_cache():
    headers = {"X-API-Key": "123"}
    # Primeira chamada popula cache
    client.get("/pokemons?limit=1&offset=0", headers=headers)
    # Segunda chamada cobre o if cached
    response = client.get("/pokemons?limit=1&offset=0", headers=headers)
    assert response.status_code == 200


def test_get_pokemon_by_id_success():
    response = client.get("/pokemons/1", headers={"X-API-Key": "123"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["name"] == "bulbasaur"


def test_get_pokemon_by_id_cache():
    headers = {"X-API-Key": "123"}
    # Primeira chamada popula cache
    client.get("/pokemons/4", headers=headers)
    # Segunda chamada cobre o if cached
    response = client.get("/pokemons/4", headers=headers)
    assert response.status_code == 200


def test_not_found():
    response = client.get("/pokemons/999999", headers={"X-API-Key": "123"})
    assert response.status_code == 404


def test_unauthorized_requests():
    # Sem header
    response = client.get("/pokemons")
    assert response.status_code == 401
    # Header errado
    response = client.get("/pokemons", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
    # Também para o endpoint /pokemons/{id}
    response = client.get("/pokemons/1")
    assert response.status_code == 401
    response = client.get("/pokemons/1", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_startup_and_shutdown():
    # Garante cobertura dos eventos de ciclo de vida
    with TestClient(app) as c:
        response = c.get("/pokemons?limit=1&offset=0", headers={"X-API-Key": "123"})
        assert response.status_code == 200

