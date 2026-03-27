import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"

def create_report(description, latitude, longitude, citizen_name="Test Citizen"):
    payload = {
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "citizen_name": citizen_name,
        "citizen_phone": "9999999999",
        "address_text": "Near Main Gate",
        "source": "web"
    }
    
    response = requests.post(f"{BASE_URL}/api/reports", json=payload)
    if response.status_code == 200:
        print(f"✅ Created report: {description[:30]}...")
        return response.json()
    else:
        print(f"❌ Failed to create report: {response.text}")
        return None

def main():
    print("🚀 Starting ticket simulation...")
    
    # Coordinates in Delhi area
    center_lat, center_lon = 28.7041, 77.1025
    
    # 1. Clustering Demo: Multiple reports for the same pothole
    print("\n📦 Simulating clustering (Same location)...")
    pothole_lat, pothole_lon = center_lat + 0.001, center_lon + 0.001
    create_report("Huge pothole near the park", pothole_lat, pothole_lon)
    create_report("Dangerous dip in the road", pothole_lat + 0.0001, pothole_lon + 0.0001)
    create_report("Road damage is causing accidents", pothole_lat - 0.0001, pothole_lon - 0.0001)
    
    # 2. Urgency Demo: High priority electricity issue
    print("\n⚡ Simulating high urgency...")
    create_report("SPARKING TRANSFORMER! DANGEROUS!", center_lat - 0.001, center_lon - 0.001)
    
    # 3. Spread: Various other issues
    print("\n🌐 Simulating various issues...")
    create_report("Water leakage from main pipe", center_lat + 0.002, center_lon - 0.002)
    create_report("Garbage pileup behind the market", center_lat - 0.002, center_lon + 0.002)
    create_report("Street light not working for 3 days", center_lat + 0.003, center_lon + 0.001)
    
    print("\n✨ Simulation complete! Check the dashboard.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        print("💡 Make sure the backend server is running at http://127.0.0.1:8000")
