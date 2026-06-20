import json
from app.redis_client import redis_client

CACHE_KEY = "promocoes:ativas"
CACHE_TTL = 300


async def buscar_ativas(conn):
    cached = await redis_client.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, nome, desconto_pct, valor_minimo, ativa FROM promocoes WHERE ativa = TRUE"
        )
        resultado = await cur.fetchall()

    await redis_client.setex(CACHE_KEY, CACHE_TTL, json.dumps(resultado))
    return resultado


async def buscar_por_id(conn, id: int):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, nome, desconto_pct, valor_minimo, ativa FROM promocoes WHERE id = %s",
            (id,)
        )
        return await cur.fetchone()


async def criar(conn, nome: str, desconto_pct: float, valor_minimo: float):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO promocoes (nome, desconto_pct, valor_minimo, ativa)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id, nome, desconto_pct, valor_minimo, ativa
            """,
            (nome, desconto_pct, valor_minimo)
        )
        resultado = await cur.fetchone()
        await conn.commit()

    await redis_client.delete(CACHE_KEY)
    return resultado


async def desativar(conn, id: int):
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE promocoes SET ativa = FALSE WHERE id = %s",
            (id,)
        )
        await conn.commit()

    await redis_client.delete(CACHE_KEY)


async def avaliar_promocoes(conn, valor_pedido: float):
    promocoes = await buscar_ativas(conn)
    aplicaveis = []
    for promo in promocoes:
        if valor_pedido >= promo["valor_minimo"]:
            desconto = round(valor_pedido * (promo["desconto_pct"] / 100), 2)
            aplicaveis.append({
                "nome": promo["nome"],
                "desconto": desconto,
                "valor_final": round(valor_pedido - desconto, 2)
            })
    return aplicaveis


async def aplicar_promocao(conn, promocao_id: int, valor_pedido: float):
    promo = await buscar_por_id(conn, promocao_id)
    if not promo:
        return None, "Promoção não encontrada"
    if not promo["ativa"]:
        return None, "Promoção inativa"
    if valor_pedido < promo["valor_minimo"]:
        return None, f"Valor mínimo é {promo['valor_minimo']}"
    desconto = round(valor_pedido * (promo["desconto_pct"] / 100), 2)
    valor_final = round(valor_pedido - desconto, 2)
    return {"desconto": desconto, "valor_final": valor_final}, None
