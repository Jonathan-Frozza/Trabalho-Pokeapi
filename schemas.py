from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PokemonBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "pikachu"})
    poke_id: Optional[int] = Field(None, json_schema_extra={"example": 25})
    data: Optional[Any] = None


class PokemonCreate(PokemonBase):
    pass


class PokemonUpdate(BaseModel):
    name: Optional[str] = None
    data: Optional[Any] = None


class PokemonOut(PokemonBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
