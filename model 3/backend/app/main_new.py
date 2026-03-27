"""
Smart PS-CRM - FastAPI Backend
Smart Public Service Customer Relationship Management System
"""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings
from app.db.base import get_db, init_db, engine
from app.models import ticket as ticket_models
from app.models.schemas import (
    CitizenReportCreate, CitizenReportResponse,
    MasterTicketResponse, TicketUpdate, ResolveTicketRequest, ResolveTicketResponse,
    DashboardStats, KanbanBoard, KanbanColumn,
    MapMarker, HeatmapPoint,
    DepartmentLeaderboardEntry, LeaderboardResponse,
    RedZoneResponse,
    ClassificationResult, SpatialClusterResult,
    StatusEnum,
    VoiceToTextRequest, VoiceToTextResponse
)
from app.services.ai_service import nlp_classifier, image_checker
from app.services.spatial_service import spatial_service, red_zone_service
from app.api import auth_router
from app.core import auth
from app.models.user import UserRole


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=\"\"\"
    Smart Public Service CRM API
    
    ## Features
    
    ### Omnichannel Intake
    - Citizen reports via web, mobile, WhatsApp, voice
    - AI-powered auto-classification
    - Sentiment analysis and urgency scoring
    
    ### Spatial Clustering
    - 30-meter radius clustering
    - Master ticket creation
    - Duplicate prevention
    
    ### Command Center
    - Real-time GIS mapping
    - Smart Kanban board with SLA timers
    - Predictive heatmaps (Red Zones)
    
    ### Accountability
    - Corruption-proof proof of work
    - Image similarity verification
    - Department leaderboards
    \"\"\",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register routers
app.include_router(auth_router.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def startup_event():
    \"\"\"Initialize database on startup.\"\"\"
    try:
        init_db()
        print(f"Server started")
        print(f"Database: {settings.DATABASE_URL}")
        print(f"AI Model: {settings.SENTENCE_TRANSFORMER_MODEL}")
        print(f"Cluster Radius: {settings.CLUSTER_RADIUS_METERS}m")
    except Exception as e:
        print(f"CRITICAL ERROR IN STARTUP: {e}")
        import traceback
        traceback.print_exc()


# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["System"])
async def health_check():
    \"\"\"Health check endpoint.\"\"\"
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "time": datetime.now().isoformat()
    }
