# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import referral, reward, admin
from app.core.database import engine, Base
from app.models import models

# Create all tables
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Referral & Rewards API",
    description="Complete backend for referral and rewards system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(referral.router)
app.include_router(reward.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {
        "status": "Backend is Running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-15T00:00:00Z"}