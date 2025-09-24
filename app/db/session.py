# app/db/session.py
import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Si prefieres cargar .env desde código (alternativa a --env-file)
try:
    from dotenv import load_dotenv
    load_dotenv()  # carga .env desde la raíz del proyecto
except Exception:
    pass

def _env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    if v == "" or v.lower() in {"none", "null"}:
        return default
    return v

DB_USER = _env("DB_USER", "root")
DB_PASSWORD = _env("DB_PASSWORD", "")
DB_HOST = _env("DB_HOST", "127.0.0.1")
DB_PORT = _env("DB_PORT", "3306")
DB_NAME = _env("DB_NAME", "rag_db")

# Escapa password por si tiene @ : / & (etc.)
PW = quote_plus(DB_PASSWORD or "")

# Params recomendados para MySQL
QS_PARAMS = "charset=utf8mb4"

DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{QS_PARAMS}"

print("DB URL ->", DATABASE_URL.replace(PW, "***"))  # debug seguro

engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # pon True si quieres ver los CREATE/SELECT en consola
    pool_pre_ping=True,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session