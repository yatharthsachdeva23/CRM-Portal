from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Citizen(Base):
    __tablename__ = 'citizens'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    lat = Column(Float)
    lon = Column(Float)
    trust_points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tickets = relationship("Ticket", back_populates="citizen")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    sub_category = Column(String)
    description = Column(Text)
    status = Column(String, default="Received")  # Received, Assigned, On Site, Resolved
    lat = Column(Float)
    lon = Column(Float)
    sentiment_score = Column(Float, default=0.0) # Used to bump priority
    cluster_id = Column(Integer, index=True, nullable=True) # To link duplicate complaints
    sla_deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    citizen_id = Column(Integer, ForeignKey('citizens.id'), nullable=True) # Nullable for anonymous/social media
    citizen = relationship("Citizen", back_populates="tickets")
    
    is_social_media = Column(Boolean, default=False)
    source = Column(String, default="Citizen Portal") # e.g. Portal, WhatsApp, X/Twitter
    image_url = Column(String, nullable=True)

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String) # e.g., Transformer, Water Pipe, Streetlight
    lat = Column(Float)
    lon = Column(Float)
    maintenance_history = Column(Text)
    last_maintained = Column(DateTime(timezone=True))
    status = Column(String, default="Active")
