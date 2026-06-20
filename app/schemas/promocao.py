from pydantic import BaseModel
from datetime import datetime


class PromocaoCreate(BaseModel):
    nome: str
    desconto_pct: float
    valor_minimo: float


class PromocaoResponse(PromocaoCreate):
    id: int
    ativa: bool

    class Config:
        from_attributes = True
