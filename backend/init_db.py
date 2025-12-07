from database import engine, Base
from models import *

def init_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Create default roles
    from sqlalchemy.orm import Session
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if roles exist
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            print("Creating default roles...")
            roles = [
                Role(name=UserRole.ADMIN, description="System administrator with full access", permissions={"all": True}),
                Role(name=UserRole.MANAGER, description="Can manage documents and schemas", permissions={"documents": ["read", "write", "delete"], "schemas": ["read", "write"]}),
                Role(name=UserRole.REVIEWER, description="Can review and approve documents", permissions={"documents": ["read", "review"]}),
                Role(name=UserRole.VIEWER, description="Can only view documents", permissions={"documents": ["read"]}),
            ]
            db.add_all(roles)
            db.commit()
            print("Default roles created!")
        else:
            print("Roles already exist, skipping...")
            
    except Exception as e:
        print(f"Error creating roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
