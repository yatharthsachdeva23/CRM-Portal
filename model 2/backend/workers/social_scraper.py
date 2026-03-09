import asyncio
from datetime import datetime, timedelta
from ..database import SessionLocal
from ..models import Ticket
from ..services.ai import classify_and_score_sentiment
from ..services.spatial import find_cluster_for_ticket

# Simulated recent X/Twitter posts for the hashtag #DelhiCityHelp
MOCK_TWEETS = [
    {
        "text": "Huge water pipe burst near Connaught Place! The whole street is flooded and it looks dangerous! #DelhiCityHelp",
        "location": {"lat": 28.6315, "lon": 77.2167} # Connaught Place
    },
    {
        "text": "Power outage in Saket sector 4 for the last 3 hours. Please fix this soon, it's very hot! #DelhiCityHelp",
        "location": {"lat": 28.5245, "lon": 77.2066} # Saket
    }
]

async def scrape_social_media_loop():
    """
    Background worker that runs periodically to fetch and process social media tags.
    """
    while True:
        db = SessionLocal()
        try:
            print("Running Digital Eyewitness Scraper...")
            for tweet in MOCK_TWEETS:
                # LLM extracts location and issue
                ai_data = classify_and_score_sentiment(tweet["text"])
                
                lat, lon = tweet["location"]["lat"], tweet["location"]["lon"]
                
                # Check for existing tickets within 20m
                cluster_id = find_cluster_for_ticket(db, lat, lon, ai_data["category"])
                
                # We check if we already processed this exact tweet by checking recent similar descriptions
                # Mock deduplication
                existing = db.query(Ticket).filter(
                    Ticket.description == tweet["text"],
                    Ticket.is_social_media == True
                ).first()
                
                if not existing:
                    new_ticket = Ticket(
                         category=ai_data["category"],
                         sub_category=ai_data["sub_category"],
                         description=tweet["text"],
                         lat=lon,
                         lon=lat,
                         source="X/Twitter",
                         sentiment_score=ai_data["sentiment_score"],
                         cluster_id=cluster_id,
                         sla_deadline=datetime.utcnow() + timedelta(hours=24),
                         is_social_media=True # Digital Eyewitness flag
                    )
                    db.add(new_ticket)
                    db.commit()
                    
                    if not new_ticket.cluster_id:
                        new_ticket.cluster_id = new_ticket.id
                        db.commit()
                        
            print("Digital Eyewitness Scrape Complete.")
        except Exception as e:
            print(f"Social Scraper Error: {e}")
        finally:
            db.close()
            
        await asyncio.sleep(3600)  # Run every hour
