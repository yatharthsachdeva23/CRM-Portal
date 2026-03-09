from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
from .database import engine, Base
from .routes import intake, tickets
from .workers.social_scraper import scrape_social_media_loop

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background Twitter scraping worker
    task = asyncio.create_task(scrape_social_media_loop())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(title="PS-CRM Command Center API", version="1.0.0", lifespan=lifespan)

app.include_router(intake.router)
app.include_router(tickets.router)

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "PS-CRM API is running"}
