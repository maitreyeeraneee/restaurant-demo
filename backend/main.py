from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
  
from database import engine, get_db, Base, SessionLocal
from models import *  # Import all models including MenuItem, ProductionEntry
from auth import get_password_hash, get_current_user
from routers.auth import router as auth_router
from routers.production import router as production_router
from routers.admin import router as admin_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Matamaal App", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(production_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "Matamaal App Running"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy"}

# Startup event to seed data
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Seed users if none
        if db.query(User).first() is None:
            admin1 = User(username="admin1", password_hash=get_password_hash("pw123"), role="admin")
            admin2 = User(username="admin2", password_hash=get_password_hash("pw123"), role="admin")
            db.add(admin1)
            db.add(admin2)
            
            cook1 = User(username="cook1", password_hash=get_password_hash("pw123"), role="cook")
            cook2 = User(username="cook2", password_hash=get_password_hash("pw123"), role="cook")
            db.add(cook1)
            db.add(cook2)
            db.commit()
            print("Sample users seeded!")
        
        admin1 = db.query(User).filter(User.username == "admin1").first()
        
        # Seed menu data (includes categories)
        print(seed_menu_data(db))
        
        print("Admins: admin1/pw123, admin2/pw123")
        print("Cooks: cook1/pw123, cook2/pw123")
        print("Menu ready. Restart server to apply.")
        
    except Exception as e:
        print(f"Startup error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

