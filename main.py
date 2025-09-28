import os
import json
import httpx
from fastapi import FastAPI, Depends, Query, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from crud import create_pokemon, get_pokemon, list_pokemons, update_pokemon, delete_pokemon
from schemas import PokemonCreate, PokemonOut, PokemonUpdate
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_fastapi_instrumentator import Instrumentator
import redis.asyncio as redis

# Configurações
USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
API_KEY = os.getenv("API_KEY", "123")
POKEAPI_BASE = os.getenv("POKEAPI_BASE", "https://pokeapi.co/api/v2")

# App FastAPI
app = FastAPI(title="Poke Proxy + CRUD API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Redis client
redis_client = None
if USE_REDIS:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        logger.warning("Redis não disponível, seguindo sem cache")
        redis_client = None


# -----------------------------
# Endpoints CRUD persistentes
# -----------------------------

@app.post("/pokemons/", response_model=PokemonOut, status_code=status.HTTP_201_CREATED, tags=["persistent"])
async def api_create_pokemon(
    p: PokemonCreate,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    created = await create_pokemon(db, p)
    return created


@app.get("/pokemons/", response_model=List[PokemonOut], tags=["persistent"])
async def api_list_pokemons(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return await list_pokemons(db, limit=limit, offset=offset)


@app.get("/pokemons/{id}", response_model=PokemonOut, tags=["persistent"])
async def api_get_pokemon(
    id: int,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    p = await get_pokemon(db, id)
    if not p:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return p


@app.put("/pokemons/{id}", response_model=PokemonOut, tags=["persistent"])
async def api_put_pokemon(
    id: int,
    payload: PokemonCreate,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    p = await get_pokemon(db, id)
    if not p:
        raise HTTPException(status_code=404, detail="Não encontrado")
    update_data = {}
    if payload.name is not None:
        update_data["name"] = payload.name
    if payload.data is not None:
        update_data["data"] = payload.data
    return await update_pokemon(db, p, PokemonUpdate(**update_data))


@app.patch("/pokemons/{id}", response_model=PokemonOut, tags=["persistent"])
async def api_patch_pokemon(
    id: int,
    payload: PokemonUpdate,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    p = await get_pokemon(db, id)
    if not p:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return await update_pokemon(db, p, payload)


@app.delete("/pokemons/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["persistent"])
async def api_delete_pokemon(
    id: int,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    p = await get_pokemon(db, id)
    if not p:
        raise HTTPException(status_code=404, detail="Não encontrado")
    await delete_pokemon(db, id)
    return None


# -----------------------------
# Endpoints externos (com cache)
# -----------------------------

@app.get("/external/pokemons", tags=["external"], summary="lista pokemons da PokeAPI (armazenado em cache)")
async def external_list_pokemons(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")

    cache_key = f"external:pokemons:{limit}:{offset}"
    cached = None
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
        except Exception:
            cached = None
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{POKEAPI_BASE}/pokemon?limit={limit}&offset={offset}")
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Erro na PokeAPI")
        payload = r.json()

    data = {"data": payload}
    if redis_client:
        try:
            await redis_client.setex(cache_key, 60, json.dumps(data))
        except Exception:
            pass
    return data


@app.get("/external/pokemons/{poke_id}", tags=["external"], summary="procura um pokemon na PokeAPI (armazenado em cache)")
async def external_get_pokemon(
    poke_id: int,
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")

    cache_key = f"external:pokemon:{poke_id}"
    cached = None
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
        except Exception:
            cached = None
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{POKEAPI_BASE}/pokemon/{poke_id}")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Pokémon não encontrado")
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Erro na PokeAPI")
        payload = r.json()

    data = {"data": payload}
    if redis_client:
        try:
            await redis_client.setex(cache_key, 60, json.dumps(data))
        except Exception:
            pass
    return data
