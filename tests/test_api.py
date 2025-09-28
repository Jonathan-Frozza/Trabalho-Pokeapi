import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import status
import sys, os

# Garantir que a raiz do projeto está no sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


# 🔹 Mock global para substituir o CRUD
@pytest.fixture(autouse=True)
def fake_crud(monkeypatch):
    from unittest.mock import AsyncMock

    fake = AsyncMock()

    # Respostas simuladas
    fake.list_pokemons.return_value = [
        {"id": 1, "name": "bulbasaur"},
        {"id": 2, "name": "pikachu"}
    ]
    fake.get_pokemon.return_value = {"id": 1, "name": "bulbasaur"}
    fake.create_pokemon.return_value = {"id": 99, "name": "meu"}
    fake.update_pokemon.return_value = {"id": 1, "name": "updated"}
    fake.delete_pokemon.return_value = True

    # Substitui diretamente no namespace do main
    monkeypatch.setattr(main, "list_pokemons", fake.list_pokemons)
    monkeypatch.setattr(main, "get_pokemon", fake.get_pokemon)
    monkeypatch.setattr(main, "create_pokemon", fake.create_pokemon)
    monkeypatch.setattr(main, "update_pokemon", fake.update_pokemon)
    monkeypatch.setattr(main, "delete_pokemon", fake.delete_pokemon)

    return fake


# 🔹 Cliente HTTP assíncrono do FastAPI
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------------- TESTES ---------------- #

@pytest.mark.asyncio
async def test_get_pokemons_success(client):
    response = await client.get(
        "/pokemons/?limit=2&offset=0",
        headers={"x-api-key": "123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Agora verificamos que é uma lista (não um objeto com "results")
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "bulbasaur"
    assert data[1]["name"] == "pikachu"


@pytest.mark.asyncio
async def test_get_pokemon_by_id_success(client):
    response = await client.get(
        "/pokemons/1",
        headers={"x-api-key": "123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "bulbasaur"


@pytest.mark.asyncio
async def test_create_pokemon_success(client):
    payload = {"poke_id": 999, "name": "meu"}
    response = await client.post(
        "/pokemons/",
        json=payload,
        headers={"x-api-key": "123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 99
    assert data["name"] == "meu"


@pytest.mark.asyncio
async def test_update_pokemon_success(client):
    payload = {"name": "updated"}
    response = await client.put(
        "/pokemons/1",
        json=payload,
        headers={"x-api-key": "123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "updated"


@pytest.mark.asyncio
async def test_delete_pokemon_success(client):
    response = await client.delete(
        "/pokemons/1",
        headers={"x-api-key": "123"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT