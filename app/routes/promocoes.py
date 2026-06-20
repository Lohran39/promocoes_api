from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.promocao import Promocao
from app.models.audit_log import AuditLog
from app.schemas.promocao import PromocaoResponse, PromocaoCreate
from app.schemas.audit_log import ApplyRequest, ApplyResponse
from app.cache import cache
import json

router = APIRouter(prefix="/promocoes", tags=["promocoes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=PromocaoResponse)
def criar(promocao: PromocaoCreate, db: Session = Depends(get_db)):
    nova = Promocao(**promocao.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    cache.clear_pattern("promocoes:*")  # Limpa cache ao criar
    return nova


@router.get("", response_model=list[PromocaoResponse])
def listar(db: Session = Depends(get_db)):
    return db.query(Promocao).filter(Promocao.ativa == True).all()


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db)):
    promo = db.query(Promocao).filter(Promocao.id == id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    promo.ativa = False
    db.commit()
    cache.clear_pattern("promocoes:*")  # Limpa cache ao deletar
    return {"mensagem": "Promoção desativada"}


@router.post("/avaliar")
def avaliar(valor_pedido: float, db: Session = Depends(get_db)):
    # Tenta obter do cache
    cache_key = f"promocoes:ativas"
    cached = cache.get(cache_key)
    
    if cached:
        aplicaveis = []
        for promo_data in cached:
            if valor_pedido >= promo_data["valor_minimo"]:
                desconto = round(valor_pedido * (promo_data["desconto_pct"] / 100), 2)
                aplicaveis.append({
                    "nome": promo_data["nome"],
                    "desconto": desconto,
                    "valor_final": round(valor_pedido - desconto, 2)
                })
        return aplicaveis or {"mensagem": "Nenhuma promoção aplicável"}
    
    # Se não estiver em cache, busca do DB
    promocoes = db.query(Promocao).filter(Promocao.ativa == True).all()
    aplicaveis = []
    
    # Armazena em cache para próximas requisições
    promo_list = []
    for promo in promocoes:
        promo_list.append({
            "id": promo.id,
            "nome": promo.nome,
            "desconto_pct": promo.desconto_pct,
            "valor_minimo": promo.valor_minimo
        })
        
        if valor_pedido >= promo.valor_minimo:
            desconto = round(valor_pedido * (promo.desconto_pct / 100), 2)
            aplicaveis.append({
                "nome": promo.nome,
                "desconto": desconto,
                "valor_final": round(valor_pedido - desconto, 2)
            })
    
    cache.set(cache_key, promo_list)
    return aplicaveis or {"mensagem": "Nenhuma promoção aplicável"}


@router.post("/apply", response_model=ApplyResponse)
def aplicar(request: ApplyRequest, db: Session = Depends(get_db)):
    promo = db.query(Promocao).filter(Promocao.id == request.promocao_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    if not promo.ativa:
        raise HTTPException(status_code=400, detail="Promoção inativa")
    if request.valor_pedido < promo.valor_minimo:
        raise HTTPException(status_code=400, detail=f"Valor mínimo é {promo.valor_minimo}")
    
    desconto = round(request.valor_pedido * (promo.desconto_pct / 100), 2)
    valor_final = round(request.valor_pedido - desconto, 2)
    
    audit = AuditLog(
        promocao_id=request.promocao_id,
        valor_pedido=request.valor_pedido,
        desconto_aplicado=desconto,
        valor_final=valor_final
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    
    return audit
