from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from ..database import get_db
from ..models import Ticket

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/")
def get_all_tickets(db: Session = Depends(get_db)):
    """Fetch all active tickets for the Command Center dashboard."""
    tickets = db.query(Ticket).order_by(desc(Ticket.created_at)).all()
    # Serialize for JSON since we don't have Pydantic models set up yet
    return [
        {
            "id": t.id,
            "category": t.category,
            "sub_category": t.sub_category,
            "description": t.description,
            "status": t.status,
            "lat": t.lat,
            "lon": t.lon,
            "sentiment_score": t.sentiment_score,
            "sla_deadline": t.sla_deadline,
            "cluster_id": t.cluster_id,
            "source": t.source,
            "created_at": t.created_at
        } for t in tickets
    ]

@router.get("/citizen/{citizen_id}")
def get_citizen_tickets(citizen_id: int, db: Session = Depends(get_db)):
    """Fetch all tickets submitted by a specific citizen."""
    tickets = db.query(Ticket).filter(Ticket.citizen_id == citizen_id).order_by(desc(Ticket.created_at)).all()
    return [
        {
            "id": t.id,
            "category": t.category,
            "description": t.description,
            "status": t.status,
            "created_at": t.created_at,
            "sla_deadline": t.sla_deadline
        } for t in tickets
    ]

@router.put("/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status: str, db: Session = Depends(get_db)):
    """Update the working status of a ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return {"message": "Status updated successfully", "status": ticket.status}
