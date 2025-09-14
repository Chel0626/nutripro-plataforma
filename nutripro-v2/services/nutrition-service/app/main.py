"""
Main FastAPI application for Nutrition Service
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Database, database
from app.routes import alimentos, calculos, pacientes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nutripro.db")
    
    global database
    database = Database(database_url)
    
    # Create tables
    await database.create_all_tables()
    
    yield
    
    # Shutdown
    # Any cleanup code here


app = FastAPI(
    title="NutriPro Nutrition Service",
    description="Microserviço de nutrição para gerenciamento de pacientes, alimentos e cálculos nutricionais",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do serviço"""
    return {
        "status": "healthy",
        "service": "nutrition-service",
        "version": "2.0.0"
    }


# Include routers
app.include_router(pacientes.router, prefix="/api/v1")
app.include_router(alimentos.router, prefix="/api/v1")
app.include_router(calculos.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "NutriPro Nutrition Service API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )