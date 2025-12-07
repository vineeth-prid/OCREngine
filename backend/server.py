from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Import database
from database import engine, Base

# Import routes
from routes import auth_routes, user_routes, tenant_routes, role_routes, schema_routes, document_routes, admin_routes, llm_routes

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting OCR Engine API...")
    print("Database tables already created via init_db.py")
    yield
    # Shutdown
    print("Shutting down OCR Engine API...")

# Initialize FastAPI app
app = FastAPI(
    title="OCR Engine API",
    description="Document-to-Structured-Data SaaS Platform with OCR + LLM Pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "OCR Engine API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/api")
async def root():
    return {
        "message": "Welcome to OCR Engine API",
        "docs": "/docs",
        "health": "/api/health"
    }

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(tenant_routes.router)
app.include_router(role_routes.router)
app.include_router(schema_routes.router)
app.include_router(document_routes.router)
app.include_router(admin_routes.router)
app.include_router(llm_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
