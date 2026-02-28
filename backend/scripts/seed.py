import os
import sys
import datetime

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database import SessionLocal, engine, Base
from backend.models import JobOffer

Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(JobOffer).count() > 0:
        print("Database already has offers. Clearing them...")
        db.query(JobOffer).delete()
        db.commit()

    print("Seeding database...")
    
    mock_offers = [
        JobOffer(title="INGENIEUR EXLOITATION", company="Engie", location="Etrez, France", url="https://engie.com/1", contract_type="CDD", published_date="28/02/2026", source="engie-jobs", status="NEW"),
        JobOffer(title="Ingénieur d'Exploitation H/F", company="Engie", location="Echirolles, France", url="https://engie.com/2", contract_type="CDI", published_date="28/02/2026", source="engie-jobs", status="NEW"),
        JobOffer(title="Ingénieur Data Pipeline", company="TotalEnergies", location="Paris, France", url="https://total.com/1", contract_type="CDI", published_date="27/02/2026", source="totalenergies", status="NEW"),
        JobOffer(title="Ingénieur Système Aéronautique", company="Airbus", location="Toulouse, France", url="https://airbus.com/1", contract_type="CDI", published_date="26/02/2026", source="airbus", status="NEW"),
        JobOffer(title="Ingénieur Méthodes Industrielles", company="Safran", location="Bordeaux, France", url="https://safran.com/1", contract_type="CDI", published_date="25/02/2026", source="safran", status="NEW"),
        JobOffer(title="Chef de Projet Déploiement", company="EDF", location="Lyon, France", url="https://edf.com/1", contract_type="CDI", published_date="24/02/2026", source="edf", status="NEW"),
    ]
    
    db.add_all(mock_offers)
    db.commit()
    print("Database seeded with 6 offers.")
    db.close()

if __name__ == "__main__":
    seed_db()
