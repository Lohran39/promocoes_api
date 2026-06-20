from fastapi import APIRouter, Depends, HTTPException
from app.db_pool import get_conn
from app.schemas.promocao import PromocaoCreate
from app.repositories import promocao_repository

router = APIRouter(prefix="/v2/promocoes", tags=["promocoes-v2"])


@router.get("")
async def listar(conn = Depends(get_conn)):
    return await promocao_repository.buscar_ativas(conn)


@router.post("")
async def criar(promocao: PromocaoCreate, conn = Depends(get_conn)):
    return await promocao_repository.criar(
        conn, promocao.nome, promocao.desconto_pct, promocao.valor_minimo
    )


@router.delete("/{id}")
async def deletar(id: int, conn = Depends(get_conn)):
    promo = await promocao_repository.buscar_por_id(conn, id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    await promocao_repository.desativar(conn, id)
    return {"mensagem": "Promoção desativada"}


@router.post("/avaliar")
async def avaliar(valor_pedido: float, conn = Depends(get_conn)):
    aplicaveis = await promocao_repository.avaliar_promocoes(conn, valor_pedido)
    return aplicaveis or {"mensagem": "Nenhuma promoção aplicável"}


from app.repositories import audit_log_repository

@router.post("/apply")
async def aplicar(request: dict, conn = Depends(get_conn)):
    from fastapi import HTTPException
    resultado, erro = await promocao_repository.aplicar_promocao(
        conn, request["promocao_id"], request["valor_pedido"]
    )
    if erro:
        raise HTTPException(status_code=400, detail=erro)

    audit = await audit_log_repository.criar(
        conn,
        promocao_id=request["promocao_id"],
        valor_pedido=request["valor_pedido"],
        desconto_aplicado=resultado["desconto"],
        valor_final=resultado["valor_final"]
    )
    return audit
