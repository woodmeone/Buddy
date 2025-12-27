from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_and_tables
from .api import personas, topics, dashboard, scripts

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
    Run on startup: Create database tables if they don't exist
    """
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Buddy Backend API is running", "docs_url": "/docs"}

# Register Routers
app.include_router(personas.router)
app.include_router(topics.router)
app.include_router(dashboard.router)
app.include_router(scripts.router)

if __name__ == "__main__":
    import uvicorn
    # Use the import string to enable reload
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8321, reload=True)
