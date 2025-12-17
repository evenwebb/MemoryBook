from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import settings
from .core.database import engine, Base
from .api.routes import images, categories, tags, search

# Create database tables (only if database is available)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database: {e}")
    print("Backend will start but database operations will fail until PostgreSQL is running.")

app = FastAPI(
    title="MemoryBook API",
    description="Self-hostable image gallery for organizing life memories",
    version="1.0.0"
)

# CORS middleware - parse comma-separated string
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(tags.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)

# Serve static files (images) - use absolute path
storage_dir = os.path.abspath(settings.UPLOAD_DIR).replace('/images', '')
if os.path.exists(storage_dir):
    app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")


@app.get("/")
async def root():
    return {
        "message": "MemoryBook API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

