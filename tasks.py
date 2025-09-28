import os
import httpx
from celery import Celery
from db import AsyncSessionLocal
from schemas import PokemonCreate
from crud import create_pokemon

CELERY_BROKER = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("tasks", broker=CELERY_BROKER)

@celery.task
def import_pokemon_by_id(poke_id: int):
    import asyncio
    asyncio.run(_import_pokemon(poke_id))

async def _import_pokemon(poke_id: int):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://pokeapi.co/api/v2/pokemon/{poke_id}")
        r.raise_for_status()
        data = r.json()
    async with AsyncSessionLocal() as db:
        create = PokemonCreate(name=data['name'], poke_id=poke_id, data=data)
        await create_pokemon(db, create)
