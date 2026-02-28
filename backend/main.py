from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    location: str = ""
    contract_type: str = ""

@app.get("/api/jobs")
def get_jobs(
    keyword: str = "", 
    location: str = "", 
    contract_type: str = "", 
    db: Session = Depends(get_db)
):
    query = db.query(JobOffer)
    
    if keyword:
        # On recherche dans le titre, l'entreprise, ET dans les mots-clés de scraping associés
        query = query.filter(
            or_(
                JobOffer.title.ilike(f"%{keyword}%"),
                JobOffer.company.ilike(f"%{keyword}%"),
                JobOffer.original_search.ilike(f"%{keyword}%")
            )
        )
    if location:
        query = query.filter(JobOffer.location.ilike(f"%{location}%"))
    if contract_type:
        query = query.filter(JobOffer.contract_type.ilike(f"%{contract_type}%"))
        
    return query.order_by(JobOffer.id.desc()).limit(150).all()

@app.post("/api/scrape")
def trigger_scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    # Combine parameters to form a powerful search query
    parts = [request.keyword]
    if request.location:
        parts.append(request.location)
    if request.contract_type:
        parts.append(request.contract_type)
        
    search_query = " ".join(parts).strip()
    
    scrapers = [
        EDFScraper(),
        TotalEnergiesScraper(),
        SafranScraper()
    ]
    
    new_offers_count = 0
    for scraper in scrapers:
        try:
            results = scraper.scrape(keyword=search_query, max_pages=3)
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
                        status="NEW",
                        original_search=search_query
                    )
                    db.add(new_job)
                    new_offers_count += 1
                else:
                    # Mettre à jour les mots-clés de recherche de l'offre existante pour qu'elle apparaisse
                    if existing.original_search:
                        if search_query not in existing.original_search:
                            existing.original_search += f" | {search_query}"
                    else:
                        existing.original_search = search_query
        except Exception as e:
            print(f"Error scraping {scraper.company_name}: {e}")
            
    db.commit()
    return {"status": "success", "new_offers_count": new_offers_count}
