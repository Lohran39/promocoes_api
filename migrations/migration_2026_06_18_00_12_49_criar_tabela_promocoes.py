from clandestino_interfaces import AbstractMigration
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()


class Migration(AbstractMigration):
    infra = None

    async def up(self) -> None:
        """Cria a tabela de promoções"""
        conn = await psycopg.AsyncConnection.connect(
            os.getenv("CLANDESTINO_POSTGRES_CONNECTION_STRING")
        )
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS promocoes (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR NOT NULL,
                        desconto_pct FLOAT NOT NULL,
                        valor_minimo FLOAT NOT NULL,
                        ativa BOOLEAN DEFAULT TRUE
                    );
                """)
                await cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_promocoes_ativa ON promocoes(ativa);
                """)
                await conn.commit()

    async def down(self) -> None:
        """Desfaz a criação da tabela"""
        conn = await psycopg.AsyncConnection.connect(
            os.getenv("CLANDESTINO_POSTGRES_CONNECTION_STRING")
        )
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("DROP TABLE IF EXISTS promocoes;")
                await conn.commit()
