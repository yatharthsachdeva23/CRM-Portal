"""
Spatial Service
Geospatial clustering and analysis for Smart PS-CRM.
Implements the 30-meter radius clustering algorithm.
"""

import math
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from geopy.distance import geodesic

from app.core.config import settings
from app.models.ticket import (
    CitizenReport, MasterTicket, RedZone, 
    TicketCategory, TicketStatus
)


class SpatialClusteringService:
    """
    Spatial clustering engine using Haversine formula.
    Groups similar complaints within a configurable radius (default 30m).
    """
    
    def __init__(self, cluster_radius_meters: float = None):
        """
        Initialize spatial clustering service.
        
        Args:
            cluster_radius_meters: Radius for clustering (default from settings)
        """
        self.cluster_radius = cluster_radius_meters or settings.CLUSTER_RADIUS_METERS
    
    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate great circle distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth's radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def find_nearby_reports(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        category: TicketCategory,
        hours: int = 72
    ) -> List[CitizenReport]:
        """
        Find existing reports within cluster radius of given location.
        
        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            category: Report category to match
            hours: Time window for recent reports
            
        Returns:
            List of nearby citizen reports
        """
        # Calculate time threshold
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        # Query recent reports of same category
        recent_reports = db.query(CitizenReport).filter(
            and_(
                CitizenReport.category == category,
                CitizenReport.created_at >= time_threshold,
                CitizenReport.master_ticket_id.isnot(None)
            )
        ).all()
        
        # Filter by distance (Haversine)
        nearby = []
        for report in recent_reports:
            if report.latitude and report.longitude:
                distance = self.haversine_distance(
                    latitude, longitude,
                    report.latitude, report.longitude
                )
                if distance <= self.cluster_radius:
                    nearby.append(report)
        
        return nearby
    
    def find_nearby_master_tickets(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        category: TicketCategory,
        exclude_closed: bool = True
    ) -> List[MasterTicket]:
        """
        Find active master tickets near the given location.
        
        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            category: Ticket category
            exclude_closed: Whether to exclude closed/resolved tickets
            
        Returns:
            List of nearby master tickets
        """
        query = db.query(MasterTicket).filter(
            MasterTicket.category == category
        )
        
        if exclude_closed:
            query = query.filter(
                ~MasterTicket.status.in_([
                    TicketStatus.CLOSED,
                    TicketStatus.VERIFIED
                ])
            )
        
        # Get all matching tickets
        tickets = query.all()
        
        # Filter by distance
        nearby = []
        for ticket in tickets:
            distance = self.haversine_distance(
                latitude, longitude,
                ticket.latitude, ticket.longitude
            )
            if distance <= self.cluster_radius:
                nearby.append((ticket, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        
        return [t[0] for t in nearby]
    
    def calculate_centroid(
        self,
        points: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        Calculate centroid of multiple points.
        
        Args:
            points: List of (latitude, longitude) tuples
            
        Returns:
            Centroid (latitude, longitude)
        """
        if not points:
            return (0.0, 0.0)
        
        # Convert to Cartesian coordinates for accurate centroid
        x_sum = y_sum = z_sum = 0.0
        
        for lat, lon in points:
            lat_rad = math.radians(lat)
            lon_rad = math.radians(lon)
            
            x_sum += math.cos(lat_rad) * math.cos(lon_rad)
            y_sum += math.cos(lat_rad) * math.sin(lon_rad)
            z_sum += math.sin(lat_rad)
        
        num_points = len(points)
        x_avg = x_sum / num_points
        y_avg = y_sum / num_points
        z_avg = z_sum / num_points
        
        # Convert back to lat/lon
        lon_centroid = math.degrees(math.atan2(y_avg, x_avg))
        hyp = math.sqrt(x_avg ** 2 + y_avg ** 2)
        lat_centroid = math.degrees(math.atan2(z_avg, hyp))
        
        return (lat_centroid, lon_centroid)
    
    def cluster_report(
        self,
        db: Session,
        report: CitizenReport
    ) -> Dict[str, Any]:
        """
        Attempt to cluster a new report with existing tickets.
        
        Args:
            db: Database session
            report: New citizen report
            
        Returns:
            Clustering result with master_ticket_id if clustered
        """
        # Find nearby master tickets
        nearby_tickets = self.find_nearby_master_tickets(
            db,
            report.latitude,
            report.longitude,
            report.category
        )
        
        if nearby_tickets:
            # Link to nearest master ticket
            master_ticket = nearby_tickets[0]
            report.master_ticket_id = master_ticket.id
            
            # Update master ticket
            master_ticket.report_count += 1
            master_ticket.upvote_count += 1
            
            # Recalculate centroid
            all_reports = db.query(CitizenReport).filter(
                CitizenReport.master_ticket_id == master_ticket.id
            ).all()
            
            points = [(r.latitude, r.longitude) for r in all_reports]
            new_lat, new_lon = self.calculate_centroid(points)
            
            master_ticket.latitude = new_lat
            master_ticket.longitude = new_lon
            
            # Boost urgency if multiple reports
            master_ticket.urgency_score = min(
                master_ticket.urgency_score + 0.5,
                10.0
            )
            
            db.commit()
            
            return {
                "clustered": True,
                "master_ticket_id": master_ticket.id,
                "ticket_number": master_ticket.ticket_number,
                "nearby_reports_count": len(all_reports),
                "message": f"Linked to existing ticket {master_ticket.ticket_number}"
            }
        
        return {
            "clustered": False,
            "master_ticket_id": None,
            "nearby_reports_count": 0,
            "message": "No nearby tickets found - will create new master ticket"
        }


class RedZoneService:
    """
    Predictive maintenance service for identifying 'Red Zones'
    where infrastructure fails repeatedly.
    """
    
    def __init__(self):
        """Initialize red zone service."""
        self.failure_threshold_30d = 3  # 3 failures in 30 days triggers red zone
        self.failure_threshold_90d = 5  # 5 failures in 90 days
    
    def analyze_location(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        category: TicketCategory,
        radius_meters: float = 100
    ) -> Dict[str, Any]:
        """
        Analyze location for recurring failures.
        
        Args:
            db: Database session
            latitude: Location latitude
            longitude: Location longitude
            category: Infrastructure category
            radius_meters: Analysis radius
            
        Returns:
            Analysis results with failure counts and risk level
        """
        from app.services.spatial_service import SpatialClusteringService
        
        spatial = SpatialClusteringService(cluster_radius_meters=radius_meters)
        
        # Count failures in different time windows
        now = datetime.now()
        
        # 30-day window
        thirty_days_ago = now - timedelta(days=30)
        tickets_30d = db.query(MasterTicket).filter(
            and_(
                MasterTicket.category == category,
                MasterTicket.created_at >= thirty_days_ago,
                MasterTicket.status.in_([TicketStatus.RESOLVED, TicketStatus.VERIFIED, TicketStatus.CLOSED])
            )
        ).all()
        
        # Filter by distance
        failures_30d = []
        for ticket in tickets_30d:
            distance = spatial.haversine_distance(
                latitude, longitude,
                ticket.latitude, ticket.longitude
            )
            if distance <= radius_meters:
                failures_30d.append(ticket)
        
        # 90-day window
        ninety_days_ago = now - timedelta(days=90)
        tickets_90d = db.query(MasterTicket).filter(
            and_(
                MasterTicket.category == category,
                MasterTicket.created_at >= ninety_days_ago,
                MasterTicket.status.in_([TicketStatus.RESOLVED, TicketStatus.VERIFIED, TicketStatus.CLOSED])
            )
        ).all()
        
        failures_90d = []
        for ticket in tickets_90d:
            distance = spatial.haversine_distance(
                latitude, longitude,
                ticket.latitude, ticket.longitude
            )
            if distance <= radius_meters:
                failures_90d.append(ticket)
        
        # Determine risk level
        failure_count_30d = len(failures_30d)
        failure_count_90d = len(failures_90d)
        
        if failure_count_30d >= 5 or failure_count_90d >= 10:
            risk_level = "critical"
        elif failure_count_30d >= 3 or failure_count_90d >= 5:
            risk_level = "high"
        elif failure_count_30d >= 2 or failure_count_90d >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            category, risk_level, failure_count_30d
        )
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "category": category.value,
            "failure_count_30d": failure_count_30d,
            "failure_count_90d": failure_count_90d,
            "risk_level": risk_level,
            "recommended_action": recommendation,
            "radius_analyzed_meters": radius_meters
        }
    
    def _generate_recommendation(
        self,
        category: TicketCategory,
        risk_level: str,
        failure_count: int
    ) -> str:
        """Generate maintenance recommendation based on analysis."""
        
        recommendations = {
            TicketCategory.ELECTRICITY: {
                "critical": "Immediate full transformer/cable replacement required. Schedule emergency maintenance.",
                "high": "Replace aging components. Upgrade to higher capacity equipment.",
                "medium": "Inspect connections and insulation. Preventive maintenance recommended.",
                "low": "Continue monitoring. Schedule routine inspection."
            },
            TicketCategory.WATER: {
                "critical": "Main pipeline replacement required. Emergency repair crew dispatch needed.",
                "high": "Section replacement recommended. Check for corrosion/blockages.",
                "medium": "Pressure testing and joint inspection. Clean blockages.",
                "low": "Routine maintenance. Monitor pressure levels."
            },
            TicketCategory.ROADS: {
                "critical": "Full resurfacing required. Close section for major repairs.",
                "high": "Patch and resurface section. Improve drainage.",
                "medium": "Pothole repair and crack sealing. Monitor condition.",
                "low": "Regular sweeping and minor repairs."
            },
            TicketCategory.SANITATION: {
                "critical": "Install permanent waste collection point. Increase pickup frequency.",
                "high": "Deploy additional bins. Increase cleaning crew visits.",
                "medium": "Optimize collection schedule. Install signage.",
                "low": "Maintain current service level."
            }
        }
        
        return recommendations.get(category, {}).get(
            risk_level,
            "Schedule inspection and maintenance as appropriate."
        )
    
    def update_or_create_red_zone(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        category: TicketCategory
    ) -> RedZone:
        """
        Update existing red zone or create new one based on analysis.
        
        Args:
            db: Database session
            latitude: Location latitude
            longitude: Location longitude
            category: Infrastructure category
            
        Returns:
            Updated or created RedZone
        """
        # Analyze location
        analysis = self.analyze_location(db, latitude, longitude, category)
        
        # Check if red zone already exists nearby
        existing = db.query(RedZone).filter(
            and_(
                RedZone.category == category,
                RedZone.latitude.between(latitude - 0.001, latitude + 0.001),
                RedZone.longitude.between(longitude - 0.001, longitude + 0.001)
            )
        ).first()
        
        if existing:
            # Update existing
            existing.failure_count_30d = analysis["failure_count_30d"]
            existing.failure_count_90d = analysis["failure_count_90d"]
            existing.risk_level = analysis["risk_level"]
            existing.recommended_action = analysis["recommended_action"]
            existing.last_failure_at = datetime.now()
        else:
            # Create new
            existing = RedZone(
                latitude=latitude,
                longitude=longitude,
                category=category,
                failure_count_30d=analysis["failure_count_30d"],
                failure_count_90d=analysis["failure_count_90d"],
                risk_level=analysis["risk_level"],
                recommended_action=analysis["recommended_action"],
                last_failure_at=datetime.now()
            )
            db.add(existing)

        # Proactive Analysis (Predictive)
        # Simple algorithm: if multiple failures in 30 days, predict next failure
        if existing.failure_count_30d > 1:
            # interval = 30 days / failure count
            days_interval = 30 / existing.failure_count_30d
            existing.predicted_failure_at = datetime.now() + timedelta(days=days_interval)
            # Deadline is 7 days before failure (minimum 1 day from now)
            existing.proactive_maintenance_deadline = max(
                existing.predicted_failure_at - timedelta(days=7),
                datetime.now() + timedelta(days=1)
            )
            existing.improvement_suggestion = f"Predicting next asset failure around {existing.predicted_failure_at.strftime('%Y-%m-%d')}. Complete maintenance before {existing.proactive_maintenance_deadline.strftime('%Y-m-%d')} to avoid service disruption."
        else:
            # For low density zones, set a conservative 30-day monitoring deadline
            existing.predicted_failure_at = None
            existing.proactive_maintenance_deadline = datetime.now() + timedelta(days=30)
            existing.improvement_suggestion = "Stable zone. Routine inspection recommended within 30 days."

        db.commit()
        db.refresh(existing)
        
        return existing
    
    def get_red_zones(
        self,
        db: Session,
        category: Optional[TicketCategory] = None,
        min_risk_level: str = "medium"
    ) -> List[RedZone]:
        """
        Get all red zones matching criteria.
        
        Args:
            db: Database session
            category: Filter by category
            min_risk_level: Minimum risk level to include
            
        Returns:
            List of RedZone objects
        """
        query = db.query(RedZone)
        
        if category:
            query = query.filter(RedZone.category == category)
        
        # Risk level ordering
        risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_level = risk_order.get(min_risk_level, 1)
        
        # Filter by risk level
        all_zones = query.all()
        filtered = [
            z for z in all_zones
            if risk_order.get(z.risk_level, 0) >= min_level
        ]
        
        # Sort by risk level (highest first)
        filtered.sort(
            key=lambda z: risk_order.get(z.risk_level, 0),
            reverse=True
        )
        
        return filtered


# Global service instances
spatial_service = SpatialClusteringService()
red_zone_service = RedZoneService()
