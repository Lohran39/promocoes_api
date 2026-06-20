from pydantic import BaseModel
from datetime import datetime


class ApplyRequest(BaseModel):
    valor_pedido: float
    promocao_id: int


class ApplyResponse(BaseModel):
    promocao_id: int
    valor_pedido: float
    desconto_aplicado: float
    valor_final: float
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    promocao_id: int | None
    valor_pedido: float
    desconto_aplicado: float
    valor_final: float
    timestamp: datetime

    class Config:
        from_attributes = True
