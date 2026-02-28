from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import engine, Base, get_db
from backend.models import JobOffer
from backend.scrapers.core import EDFScraper, TotalEnergiesScraper, SafranScraper

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Hunter OS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    keyword: str

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(JobOffer).order_by(JobOffer.id.desc()).all()

@app.post("/api/scrape")
def trigger_scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    keyword = request.keyword
    
    scrapers = [
        EDFScraper(),
        TotalEnergiesScraper(),
        SafranScraper()
    ]
    
    new_offers_count = 0
    for scraper in scrapers:
        try:
            results = scraper.scrape(keyword=keyword, max_pages=1)
            for r in results:
                existing = db.query(JobOffer).filter(JobOffer.url == r.url).first()
                if not existing:
                    new_job = JobOffer(
                        title=r.titre,
                        company=r.entreprise,
                        location=r.lieu,
                        url=r.url,
                        contract_type=r.contrat,
                        published_date=r.date_publication,
                        source=r.source,
                        status="NEW"
                    )
                    db.add(new_job)
                    new_offers_count += 1
        except Exception as e:
            print(f"Error scraping {scraper.company_name}: {e}")
            
    db.commit()
    return {"status": "success", "new_offers_count": new_offers_count}
