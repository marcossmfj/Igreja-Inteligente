from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import database, models
from .routes import membros, auth, webhooks, payments, escalas, master, docs, visitantes
from .automation import tasks
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o Robô Agendador no startup
    tasks.start_scheduler()
    print("🚀 Robô de Automação Master Iniciado!")
    yield
    # Lógica de shutdown (se necessário) pode ir aqui

app = FastAPI(title="SaaS Master Igreja Inteligente", version="3.0.0", lifespan=lifespan)

# Configuração de CORS (Liberando acesso para a VPS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas
app.include_router(auth.router)
app.include_router(master.router)
app.include_router(payments.router)
app.include_router(membros.router)
app.include_router(visitantes.router)
app.include_router(escalas.router)
app.include_router(webhooks.router)
app.include_router(docs.router)

# Frontend e Assets Dinâmicos
app.mount("/dashboard", StaticFiles(directory="app/static", html=True), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
def read_root():
    return RedirectResponse(url="/dashboard/")
