import sys
import os
import sqlite3

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import engine, Base
from app.models.ticket import RedZone

def force_init():
    db_path = "smart_ps_crm.db"
    if os.path.exists(db_path):
        print(f"Deleting existing DB: {db_path}")
        os.remove(db_path)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Verifying 'red_zones' schema...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(red_zones)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns in red_zones: {columns}")
    
    required = ["predicted_failure_at", "proactive_maintenance_deadline", "improvement_suggestion"]
    for col in required:
        if col in columns:
            print(f"✅ Found column: {col}")
        else:
            print(f"❌ MISSING column: {col}")
    
    conn.close()

if __name__ == "__main__":
    force_init()
