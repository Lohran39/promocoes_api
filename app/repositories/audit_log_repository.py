async def criar(conn, promocao_id: int, valor_pedido: float, desconto_aplicado: float, valor_final: float):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO audit_logs (promocao_id, valor_pedido, desconto_aplicado, valor_final, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id, promocao_id, valor_pedido, desconto_aplicado, valor_final, timestamp
            """,
            (promocao_id, valor_pedido, desconto_aplicado, valor_final)
        )
        resultado = await cur.fetchone()
        await conn.commit()
        return resultado


async def buscar_historico(conn, limite: int = 10):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id, promocao_id, valor_pedido, desconto_aplicado, valor_final, timestamp
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limite,)
        )
        return await cur.fetchall()


async def buscar_por_promocao(conn, promocao_id: int):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id, promocao_id, valor_pedido, desconto_aplicado, valor_final, timestamp
            FROM audit_logs
            WHERE promocao_id = %s
            ORDER BY timestamp DESC
            """,
            (promocao_id,)
        )
        return await cur.fetchall()
