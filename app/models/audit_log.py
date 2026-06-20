from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id             = Column(Integer, primary_key=True, index=True)
    promocao_id    = Column(Integer, nullable=True)
    valor_pedido   = Column(Float, nullable=False)
    desconto_aplicado = Column(Float, nullable=False)
    valor_final    = Column(Float, nullable=False)
    timestamp      = Column(DateTime, default=datetime.utcnow, index=True)
