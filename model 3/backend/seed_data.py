"""
Seed Data Script
Initialize database with sample departments and test data.
"""

from sqlalchemy.orm import Session
from app.db.base import SessionLocal, init_db
from app.models.ticket import Department, Worker, TicketCategory


def seed_departments(db: Session):
    """Create default departments."""
    departments = [
        {
            "name": "Electricity Department",
            "code": "ELEC",
            "category": TicketCategory.ELECTRICITY
        },
        {
            "name": "Water Supply Department",
            "code": "WATER",
            "category": TicketCategory.WATER
        },
        {
            "name": "Roads & Infrastructure",
            "code": "ROADS",
            "category": TicketCategory.ROADS
        },
        {
            "name": "Sanitation & Waste Management",
            "code": "SANI",
            "category": TicketCategory.SANITATION
        }
    ]
    
    for dept_data in departments:
        existing = db.query(Department).filter(
            Department.code == dept_data["code"]
        ).first()
        
        if not existing:
            dept = Department(**dept_data)
            db.add(dept)
            print(f" Created department: {dept.name}")
    
    db.commit()


def seed_workers(db: Session):
    """Create sample workers."""
    workers = [
        {"name": "Rajesh Kumar", "employee_id": "ELEC001", "dept_code": "ELEC"},
        {"name": "Suresh Patel", "employee_id": "ELEC002", "dept_code": "ELEC"},
        {"name": "Amit Sharma", "employee_id": "WATER001", "dept_code": "WATER"},
        {"name": "Priya Singh", "employee_id": "WATER002", "dept_code": "WATER"},
        {"name": "Vikram Rao", "employee_id": "ROADS001", "dept_code": "ROADS"},
        {"name": "Deepak Verma", "employee_id": "ROADS002", "dept_code": "ROADS"},
        {"name": "Anita Desai", "employee_id": "SANI001", "dept_code": "SANI"},
        {"name": "Mohammed Ali", "employee_id": "SANI002", "dept_code": "SANI"}
    ]
    
    for worker_data in workers:
        existing = db.query(Worker).filter(
            Worker.employee_id == worker_data["employee_id"]
        ).first()
        
        if not existing:
            # Find department
            dept = db.query(Department).filter(
                Department.code == worker_data["dept_code"]
            ).first()
            
            if dept:
                worker = Worker(
                    name=worker_data["name"],
                    employee_id=worker_data["employee_id"],
                    department_id=dept.id
                )
                db.add(worker)
                print(f" Created worker: {worker.name} ({dept.name})")
    
    db.commit()


def main():
    """Main seed function."""
    print(" Seeding database...")
    
    init_db()
    db = SessionLocal()
    
    try:
        seed_departments(db)
        seed_workers(db)
        print(" Database seeded successfully!")
    except Exception as e:
        print(f" Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
