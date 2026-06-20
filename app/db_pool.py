import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("CLANDESTINO_POSTGRES_CONNECTION_STRING")


async def get_conn():
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        row_factory=dict_row  # retorna resultados como dict, não tupla
    ) as conn:
        yield conn
