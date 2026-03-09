from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Ticket
import math

def get_distance_meters(lat1, lon1, lat2, lon2):
    # Simple Haversine or Pythagorean for small distances
    R = 6371e3
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def find_cluster_for_ticket(db: Session, lat: float, lon: float, category: str, radius_m: int = 20):
    """
    Finds if there's an existing active ticket of the same category within the given radius (in meters).
    Uses a rough bounding box query first in SQLite, then maths the distance.
    """
    deg_diff = radius_m / 111000.0
    
    nearby_tickets = db.query(Ticket).filter(
        Ticket.status.in_(["Received", "Assigned", "On Site"]),
        Ticket.category == category,
        Ticket.lat.between(lat - deg_diff, lat + deg_diff),
        Ticket.lon.between(lon - deg_diff, lon + deg_diff)
    ).all()
    
    for t in nearby_tickets:
         if t.lat and t.lon and get_distance_meters(lat, lon, t.lat, t.lon) <= radius_m:
             return t.cluster_id if t.cluster_id else t.id
             
    return None

def get_tickets_for_routing(db: Session, base_lat: float, base_lon: float, radius_m: int = 200):
    """
    Retrieves low-priority tickets within 200m of a high-priority dispatch.
    """
    deg_diff = radius_m / 111000.0
    
    nearby_tickets = db.query(Ticket).filter(
        Ticket.status.in_(["Received", "Assigned"]),
        Ticket.lat.between(base_lat - deg_diff, base_lat + deg_diff),
        Ticket.lon.between(base_lon - deg_diff, base_lon + deg_diff)
    ).all()
    
    valid_tickets = []
    for t in nearby_tickets:
         if t.lat and t.lon and get_distance_meters(base_lat, base_lon, t.lat, t.lon) <= radius_m:
             valid_tickets.append(t)
             
    return valid_tickets
