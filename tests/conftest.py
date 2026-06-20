import pytest
import asyncio
import psycopg
from unittest.mock import AsyncMock
from psycopg.rows import dict_row
from fastapi.testclient import TestClient
from app.main import app
from app.db_pool import get_conn
import app.repositories.promocao_repository as promo_repo

TEST_DATABASE_URL = "postgresql://postgres:lh39@127.0.0.1:5432/promocoes_test_db"


async def get_test_conn():
    async with await psycopg.AsyncConnection.connect(
        TEST_DATABASE_URL, row_factory=dict_row
    ) as conn:
        yield conn


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Substitui o Redis real por um mock — sempre simula cache vazio."""
    mock = AsyncMock()
    mock.get.return_value = None
    monkeypatch.setattr(promo_repo, "redis_client", mock)
    yield


@pytest.fixture(autouse=True)
def setup_database():
    """Cria as tabelas antes de cada teste e limpa depois."""
    async def _setup():
        conn = await psycopg.AsyncConnection.connect(TEST_DATABASE_URL)
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
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        promocao_id INTEGER,
                        valor_pedido FLOAT NOT NULL,
                        desconto_aplicado FLOAT NOT NULL,
                        valor_final FLOAT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    );
                """)
                await conn.commit()

    asyncio.run(_setup())

    app.dependency_overrides[get_conn] = get_test_conn
    yield

    async def _teardown():
        conn = await psycopg.AsyncConnection.connect(TEST_DATABASE_URL)
        async with conn:
            async with conn.cursor() as cur:
                await cur.execute("TRUNCATE promocoes, audit_logs RESTART IDENTITY CASCADE;")
                await conn.commit()

    asyncio.run(_teardown())
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
