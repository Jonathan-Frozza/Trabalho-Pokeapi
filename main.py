import os
import json
import redis.asyncio as redis
import httpx
from fastapi import FastAPI, Query, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager


USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"

redis_client = None
if USE_REDIS:
    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = redis.from_url("redis://localhost", decode_responses=True)
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/pokemons")
@limiter.limit("100/minute")  
async def get_pokemons(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    x_api_key: str = Header(None),
):
    if x_api_key != os.getenv("API_KEY", "123"):
        raise HTTPException(status_code=401, detail="Não autorizado")

    cache_key = f"pokemons:{limit}:{offset}"
    cached = None

    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
        except Exception:
            cached = None

    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://pokeapi.co/api/v2/pokemon?limit={limit}&offset={offset}"
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erro na API externa")

        data = {"data": response.json()}

    if redis_client:
        try:
            await redis_client.setex(cache_key, 60, json.dumps(data))
        except Exception:
            pass

    return data


@app.get("/pokemons/{id}")
@limiter.limit("100/minute")
async def get_pokemon(request: Request, id: int, x_api_key: str = Header(None)):
    if x_api_key != os.getenv("API_KEY", "123"):
        raise HTTPException(status_code=401, detail="Não autorizado")

    cache_key = f"pokemon:{id}"
    cached = None

    
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
        except Exception:
            cached = None

    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Pokémon não encontrado")
        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erro na API externa")

        data = {"data": response.json()}

   
    if redis_client:
        try:
            await redis_client.setex(cache_key, 60, json.dumps(data))
        except Exception:
            pass

    return data
