from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os

from ..database import get_db
from ..models import Ticket, Citizen
from ..services.ai import process_voice_to_text, classify_and_score_sentiment
from ..services.spatial import find_cluster_for_ticket

router = APIRouter(prefix="/intake", tags=["Intake"])

@router.post("/submit")
async def submit_ticket(
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    citizen_id: int = Form(None),
    source: str = Form("Citizen Portal"),
    audio_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Standard submission endpoint for citizen portal and mobile app.
    Handles optional text, audio and images.
    """
    final_text = description
    
    # Process Voice-to-Text via whisper/bhashini
    if audio_file:
        file_location = f"temp_{audio_file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(audio_file.file.read())
        
        transcribed_text = process_voice_to_text(file_location)
        final_text = f"{description} | Audio: {transcribed_text}"
        os.remove(file_location) # cleanup
        
    # AI Classification
    ai_data = classify_and_score_sentiment(final_text)
    
    # Check for duplicate high-priority cluster within 20 meters
    cluster_id = find_cluster_for_ticket(db, lat, lon, ai_data["category"], radius_m=20)
    
    # SLA Logic (mocked)
    sla_deadline = datetime.utcnow() + timedelta(hours=24)
    if ai_data["sentiment_score"] > 0.8:
        sla_deadline = datetime.utcnow() + timedelta(hours=4) # bump priority
        
    new_ticket = Ticket(
        category=ai_data["category"],
        sub_category=ai_data["sub_category"],
        description=final_text,
        lat=lat,
        lon=lon,
        source=source,
        sentiment_score=ai_data["sentiment_score"],
        cluster_id=cluster_id,
        sla_deadline=sla_deadline,
        citizen_id=citizen_id
    )
    
    # Award Trust Points if citizen exists
    if citizen_id:
        citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
        if citizen:
            citizen.trust_points += 10
            
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    # Update cluster ID if it wasn't clustered
    if not new_ticket.cluster_id:
        new_ticket.cluster_id = new_ticket.id
        db.commit()
        db.refresh(new_ticket)
        
    return {"message": "Ticket created", "ticket": new_ticket}

@router.post("/whatsapp")
async def whatsapp_webhook(payload: dict, db: Session = Depends(get_db)):
    """
    Omnichannel Intake webhook endpoint for WhatsApp bots.
    """
    # Parse payload according to WhatsApp API, then call same logic as above
    # Example parsing
    phone_number = payload.get("from")
    text = payload.get("body")
    location = payload.get("location", {"lat": 28.6139, "lon": 77.2090}) # Default to Delhi
    
    # Find or create citizen by phone
    citizen = db.query(Citizen).filter(Citizen.phone == phone_number).first()
    if not citizen:
        citizen = Citizen(phone=phone_number, name="WhatsApp User", lat=location['lat'], lon=location['lon'])
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        
    ai_data = classify_and_score_sentiment(text)
    cluster_id = find_cluster_for_ticket(db, location["lat"], location["lon"], ai_data["category"])
    
    new_ticket = Ticket(
         category=ai_data["category"],
         sub_category=ai_data["sub_category"],
         description=text,
         lat=location['lat'],
         lon=location['lon'],
         source="WhatsApp",
         sentiment_score=ai_data["sentiment_score"],
         cluster_id=cluster_id,
         sla_deadline=datetime.utcnow() + timedelta(hours=24),
         citizen_id=citizen.id
    )
    db.add(new_ticket)
    db.commit()
    
    if not new_ticket.cluster_id:
        new_ticket.cluster_id = new_ticket.id
        db.commit()
        
    return {"status": "success", "message": "Ticket logged from WhatsApp"}
