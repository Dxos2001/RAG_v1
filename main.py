from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.db import loadModels  # <-- importa modelos
from app.controller.userController import router as user_router  # importa tu router de usuario
from app.controller.authController import router as auth_router  # importa tu router de autenticación


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

# Incluye todos los routers de tus controladores
app.include_router(user_router)
app.include_router(auth_router)
# Si tienes más controladores, agrégalos aquí

@app.get("/health", tags=["Health"])
def health():
    return {"ok": True}