import sqlite3
import datetime
import uvicorn
import sys
import io
import os

# Add backend to path for app import
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def insert_data():
    db_path = "backend/smart_ps_crm.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    
    try:
        # Check if we already have tickets
        cursor.execute("SELECT count(*) FROM master_tickets")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Database already has {count} tickets. Skipping insertion.")
            return

        print("Inserting sample tickets...")
        
        # Electricity Ticket
        cursor.execute("""
            INSERT INTO master_tickets (
                ticket_number, category, description, latitude, longitude, 
                status, priority, urgency_score, sla_hours, created_at, 
                report_count, upvote_count, verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('CRM-20260325-0001', 'Electricity', 'Sparking transformer near the main gate', 
              28.7041, 77.1025, 'reported', 'high', 8.5, 24, now, 1, 0, 'pending'))
        
        master_id_elec = cursor.lastrowid
        
        # Roads Ticket
        cursor.execute("""
            INSERT INTO master_tickets (
                ticket_number, category, description, latitude, longitude, 
                status, priority, urgency_score, sla_hours, created_at, 
                report_count, upvote_count, verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('CRM-20260325-0002', 'Roads', 'Dangerous pothole on main road', 
              28.7051, 77.1035, 'reported', 'medium', 6.0, 48, now, 1, 0, 'pending'))
        
        master_id_roads = cursor.lastrowid
        
        # Link reports
        cursor.execute("""
            INSERT INTO citizen_reports (
                description, latitude, longitude, category, source, 
                created_at, master_ticket_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Sparking wires', 28.7041, 77.1025, 'Electricity', 'web', now, master_id_elec))
        
        cursor.execute("""
            INSERT INTO citizen_reports (
                description, latitude, longitude, category, source, 
                created_at, master_ticket_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Huge pothole', 28.7051, 77.1035, 'Roads', 'web', now, master_id_roads))
        
        conn.commit()
        print("Sample data successfully inserted!")
    except Exception as e:
        print(f"Error during data insertion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Force UTF-8 encoding for Windows stability
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        os.environ["PYTHONUTF8"] = "1"

    insert_data()
    
    print("Starting backend server...")
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000)
