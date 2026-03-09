import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const LiveMap = ({ tickets = [], showPredictive = false }) => {
    // Center tightly on Delhi
    const [position] = useState([28.6139, 77.2090]);

    const PREDICTIVE_RED_ZONES = showPredictive ? [
        { lat: 28.6139, lon: 77.2090, radius: 2000, reason: "Fast Accumulating Electricity Reports in Central Delhi" },
        { lat: 28.5245, lon: 77.2066, radius: 1500, reason: "Predicted Water Pressure Failure (Saket Area)" }
    ] : [];

    return (
        <MapContainer
            center={position}
            zoom={11}
            scrollWheelZoom={true}
            className="h-full w-full absolute inset-0 rounded-b-xl z-0"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />

            {/* Predictive Red Zones */}
            {PREDICTIVE_RED_ZONES.map((zone, idx) => (
                <Circle
                    key={`zone-${idx}`}
                    center={[zone.lat, zone.lon]}
                    radius={zone.radius}
                    pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.2 }}
                >
                    <Popup>
                        <div className="font-bold text-red-600 tracking-wide uppercase">AI Predictive Alert</div>
                        <div className="text-sm font-medium mt-1">{zone.reason}</div>
                        <div className="text-xs text-gray-500 mt-2 italic">Suggested Action: Pre-deploy maintenance crews.</div>
                    </Popup>
                </Circle>
            ))}

            {/* Clustered Ticket Markers */}
            {tickets.map(ticket => {
                // Only render if we have coordinates
                if (!ticket.lat || !ticket.lon) return null;

                const isHighPriority = ticket.sentiment_score > 0.7;

                return (
                    <Marker key={ticket.id} position={[ticket.lat, ticket.lon]}>
                        <Popup>
                            <div className="font-semibold text-gray-800">{ticket.category} - #{ticket.id}</div>
                            <div className="text-xs text-gray-500 mt-1">Source: <span className="font-semibold text-indigo-500">{ticket.source}</span></div>
                            <div className="text-xs text-gray-600 mt-1">Status: <span className="font-bold uppercase">{ticket.status}</span></div>
                            <div className="text-xs text-gray-600 mt-1 truncate max-w-[200px]">"{ticket.description}"</div>

                            <div className={`text-xs mt-2 px-2 py-1 inline-block rounded font-bold ${isHighPriority ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                {isHighPriority ? 'HIGH PRIORITY' : 'STANDARD'}
                            </div>
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
};

export default LiveMap;
