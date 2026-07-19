import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

# Local imports
from database import engine, get_db
import models
from routers import auth, cases

from contextlib import asynccontextmanager

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for safe database initialization on startup."""
    try:
        if engine:
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created/verified successfully on startup.")
        else:
            logger.warning("Database engine is not configured!")
    except Exception as e:
        logger.error(f"Failed to initialize database tables during startup: {e}")
    
    yield
    
    # Optional shutdown logic can go here

app = FastAPI(title="JusticeFlowX API", version="3.0", lifespan=lifespan)

# CORS Middleware (Allow requests from Nginx frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change to the actual frontend domain (e.g., http://localhost)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import auth, cases, law

# Include Routers
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(law.router)

# --- GLOBAL ROUTES ---

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and DB status."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    return {
        "status": "online",
        "service": "JusticeFlowX Backend",
        "database": db_status
    }
