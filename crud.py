from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models_db import Pokemon
from schemas import PokemonCreate, PokemonUpdate


# 🔹 Criar Pokémon
async def create_pokemon(db: AsyncSession, obj: PokemonCreate) -> Pokemon:
    p = Pokemon(name=obj.name, poke_id=obj.poke_id, data=obj.data)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


# 🔹 Buscar por ID
async def get_pokemon(db: AsyncSession, id: int) -> Optional[Pokemon]:
    return await db.get(Pokemon, id)


# 🔹 Buscar por poke_id
async def get_by_poke_id(db: AsyncSession, poke_id: int) -> Optional[Pokemon]:
    q = await db.execute(select(Pokemon).where(Pokemon.poke_id == poke_id))
    return q.scalars().first()


# 🔹 Listar Pokémons
async def list_pokemons(db: AsyncSession, limit: int = 20, offset: int = 0) -> List[Pokemon]:
    q = await db.execute(select(Pokemon).offset(offset).limit(limit))
    return q.scalars().all()


# 🔹 Atualizar Pokémon
async def update_pokemon(db: AsyncSession, db_obj: Pokemon, obj_in: PokemonUpdate) -> Pokemon:
    if obj_in.name is not None:
        db_obj.name = obj_in.name
    if obj_in.data is not None:
        db_obj.data = obj_in.data
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# 🔹 Deletar Pokémon
async def delete_pokemon(db: AsyncSession, id: int) -> bool:
    q = await db.execute(delete(Pokemon).where(Pokemon.id == id))
    await db.commit()
    return q.rowcount > 0  # Retorna True se deletou algo
