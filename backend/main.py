from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend.models import JobOffer

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Hunter OS API")

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(JobOffer).all()
