# Pokémon Proxy API + CRUD (FastAPI)

API em **FastAPI** que consome a [PokeAPI](https://pokeapi.co/) e adiciona recursos extras:

Projeto completo com:
- FastAPI + endpoints de leitura contra PokeAPI (cached) e CRUD persistido (Postgres + SQLAlchemy async)
- Redis cache
- Autenticação via `x-api-key`
- Rate limiting (slowapi)
- Migrations (Alembic)
- Celery worker example (Redis broker)
- Docker & docker-compose (api, redis, postgres)
- Podman (alternativa ao Docker)
- Kubernetes manifests (examples)
- Tests (pytest + pytest-asyncio)

## Como rodar localmente com Docker

```bash
docker-compose up --build
```

Rodar migrations (após db subir):
```bash
docker-compose exec api alembic upgrade head
```

Acessar docs:
```
http://localhost:8000/docs
```

> ⚠️ **Use o header de autenticação**  
> `x-api-key: 123`

---

## Como rodar localmente com Podman

```bash
podman-compose up --build
```

Rodar migrations (após db subir):
```bash
podman-compose exec api alembic upgrade head
```

Acessar docs:
```
http://localhost:8000/docs
```

---

## Testes

```bash
pytest
```

---

## Exemplo de requisição e resposta da API

### Listar Pokémons (via PokeAPI Proxy)
**Request:**
```http
GET /pokemons?limit=2&offset=0
X-API-Key: 123
```

**Response:**
```json
{
  "data": {
    "results": [
      { "name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/" },
      { "name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/" }
    ]
  }
}
```

---

### Detalhar Pokémon
**Request:**
```http
GET /pokemons/25
X-API-Key: 123
```

**Response:**
```json
{
  "data": {
    "id": 25,
    "name": "pikachu",
    "height": 4,
    "weight": 60,
    "types": [
      { "slot": 1, "type": { "name": "electric", "url": "https://pokeapi.co/api/v2/type/13/" } }
    ]
  }
}
```

---

## CRUD de Pokémons (Banco de Dados)

### Criar Pokémon (POST)
```bash
curl -X POST http://localhost:8000/pokemons \
  -H "Content-Type: application/json" \
  -H "x-api-key: 123" \
  -d '{
    "name": "Raichu",
    "data": { "type": "electric" }
  }'
```

**Resposta (201 Created):**
```json
{
  "id": 1,
  "name": "Raichu",
  "data": { "type": "electric" },
  "created_at": "2025-09-26T21:53:30.440Z",
  "updated_at": null
}
```

---

### Atualizar Pokémon (PUT)
```bash
curl -X PUT http://localhost:8000/pokemons/1 \
  -H "Content-Type: application/json" \
  -H "x-api-key: 123" \
  -d '{
    "name": "Raichu",
    "data": { "type": "electric", "evolution": "Pichu -> Pikachu -> Raichu" }
  }'
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "name": "Raichu",
  "data": {
    "type": "electric",
    "evolution": "Pichu -> Pikachu -> Raichu"
  },
  "created_at": "2025-09-26T21:53:30.440Z",
  "updated_at": "2025-09-26T22:10:12.123Z"
}
```

---

### Buscar Pokémon (GET)
```bash
curl -X GET http://localhost:8000/pokemons/1 \
  -H "x-api-key: 123"
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "name": "Raichu",
  "data": {
    "type": "electric",
    "evolution": "Pichu -> Pikachu -> Raichu"
  },
  "created_at": "2025-09-26T21:53:30.440Z",
  "updated_at": "2025-09-26T22:10:12.123Z"
}
```

---

### Deletar Pokémon (DELETE)
```bash
curl -X DELETE http://localhost:8000/pokemons/1 \
  -H "x-api-key: 123"
```

**Resposta (200 OK):**
```json
{ "message": "Pokemon deleted successfully" }
```
