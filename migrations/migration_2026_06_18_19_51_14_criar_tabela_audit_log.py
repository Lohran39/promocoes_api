from clandestino_interfaces import AbstractMigration
from dotenv import load_dotenv
import psycopg
import os

load_dotenv()


class Migration(AbstractMigration):
    infra = None

    async def up(self) -> None:
        """Cria a tabela de audit_log"""
        conn = await psycopg.AsyncConnection.connect(
            os.getenv("CLANDESTINO_POSTGRES_CONNECTION_STRING")
        )
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        promocao_id INTEGER,
                        valor_pedido FLOAT NOT NULL,
                        desconto_aplicado FLOAT NOT NULL,
                        valor_final FLOAT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                await cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
                """)
                await cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_promocao_id ON audit_logs(promocao_id);
                """)
                await conn.commit()

    async def down(self) -> None:
        """Desfaz a criação da tabela"""
        conn = await psycopg.AsyncConnection.connect(
            os.getenv("CLANDESTINO_POSTGRES_CONNECTION_STRING")
        )
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("DROP TABLE IF EXISTS audit_logs;")
                await conn.commit()
