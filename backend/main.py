from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables, SessionLocal
from .api import personas, topics, dashboard, scripts, ai
from .services.crawler import crawler_service
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BuddyApp")

def sync_job():
    """Background sync job runner"""
    logger.info("Starting background synchronization job...")
    with SessionLocal() as session:
        crawler_service.sync_all_sources(session)
    logger.info("Background synchronization completed.")

# Initialize FastAPI App
app = FastAPI(title="Buddy System API", version="0.1.0")

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite Dev Server
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Run on startup: Create database tables and start background scheduler
    """
    create_db_and_tables()
    
    # Initialize Scheduler
    scheduler = BackgroundScheduler()
    # Run sync every day at 00:00 and 12:00
    scheduler.add_job(sync_job, 'cron', hour='0,12')
    scheduler.start()
    
    logger.info("Backend services started and scheduler is active.")

@app.get("/")
def read_root():
    return {"message": "Buddy Backend API is running", "docs_url": "/docs"}

# Register Routers
app.include_router(personas.router)
app.include_router(topics.router)
app.include_router(dashboard.router)
app.include_router(scripts.router)
app.include_router(ai.router)

if __name__ == "__main__":
    import uvicorn
    # Use the import string to enable reload
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8321, reload=True)
