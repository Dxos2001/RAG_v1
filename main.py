from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.db import loadModels  # <-- importa modelos
#from app.controllers import ask_controller, ingest_controller  # y tus otros routers

app = FastAPI(title="Thesis RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # crea tablas cuando haya MYSQL_URL real (en Railway)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#app.include_router(ask_controller.router)
#app.include_router(ingest_controller.router)

@app.get("/health", tags=["Health"])
def health():
    return {"ok": True}