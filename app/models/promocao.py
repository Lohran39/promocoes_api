from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class Promocao(Base):
    __tablename__ = "promocoes"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String, nullable=False)
    desconto_pct = Column(Float, nullable=False)
    valor_minimo = Column(Float, nullable=False)
    ativa        = Column(Boolean, default=True)

