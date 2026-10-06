from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import admin_router, aluno_router, auth_router, prof_router

app = FastAPI(
    title="EduCollab API - IA Engine",
    description="Backend de Inteligência Artificial - Atividade Extensionista IV",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()

# Essencial para conectar o React (Porta 5173) ao FastAPI (Porta 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(aluno_router.router)
app.include_router(prof_router.router)

@app.get("/", tags=["Health Check"])
def root():
    return {"status": "EduCollab IA Microservice Operacional"}