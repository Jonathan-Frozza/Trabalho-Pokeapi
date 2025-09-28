from sqlalchemy import Column, Integer, String, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Pokemon(Base):
    __tablename__ = "pokemons"
    id = Column(Integer, primary_key=True, index=True)
    poke_id = Column(Integer, index=True, nullable=True)
    name = Column(String, index=True, nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("poke_id", name="uq_poke_id"),)
