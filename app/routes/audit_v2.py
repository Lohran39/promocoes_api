from fastapi import APIRouter, Depends
from app.db_pool import get_conn
from app.repositories import audit_log_repository

router = APIRouter(prefix="/v2/audit", tags=["audit-v2"])


@router.get("/history")
async def historico(limite: int = 10, conn = Depends(get_conn)):
    return await audit_log_repository.buscar_historico(conn, limite)


@router.get("/history/{promocao_id}")
async def historico_por_promocao(promocao_id: int, conn = Depends(get_conn)):
    return await audit_log_repository.buscar_por_promocao(conn, promocao_id)
