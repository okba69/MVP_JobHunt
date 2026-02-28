import datetime
import sys
import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel

from backend.database import engine, Base, get_db
from backend.models import JobOffer, ScrapeCache
from backend.scrapers.core import EDFScraper, TotalEnergiesScraper, SafranScraper, AirbusScraper

# Ajouter le répertoire scrapers/tests au path pour importer Indeed et LinkedIn
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scrapers", "tests"))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Hunter OS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Durée du cache (en heures) ──────────────────────────────────────────────
CACHE_DURATION_HOURS = 24


class ScrapeRequest(BaseModel):
    keyword: str


# ─── GET /api/jobs — Filtrage local instantané ────────────────────────────────

@app.get("/api/jobs")
def get_jobs(
    keyword: str = "",
    location: str = "",
    contract_type: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(JobOffer)

    if keyword:
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

    return query.order_by(JobOffer.id.desc()).all()


# ─── Helpers : Cache intelligent ──────────────────────────────────────────────

def is_keyword_fresh(db: Session, keyword: str) -> bool:
    """Vérifie si le mot-clé a déjà été scrapé dans les dernières CACHE_DURATION_HOURS heures."""
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=CACHE_DURATION_HOURS)
    cache_entry = (
        db.query(ScrapeCache)
        .filter(ScrapeCache.keyword == keyword.lower())
        .filter(ScrapeCache.last_scraped_at >= cutoff)
        .first()
    )
    return cache_entry is not None


def update_cache(db: Session, keyword: str, source: str, count: int):
    """Met à jour le timestamp de cache pour un mot-clé donné."""
    existing = (
        db.query(ScrapeCache)
        .filter(ScrapeCache.keyword == keyword.lower(), ScrapeCache.source == source)
        .first()
    )
    if existing:
        existing.last_scraped_at = datetime.datetime.utcnow()
        existing.offers_found = count
    else:
        db.add(ScrapeCache(
            keyword=keyword.lower(),
            source=source,
            offers_found=count
        ))


def save_offer(db: Session, r, source: str, search_query: str) -> bool:
    """Sauvegarde une offre dans la base. Retourne True si c'est une nouvelle offre."""
    # Construire l'URL de dédup
    url = getattr(r, "url", "") or ""
    if not url:
        return False

    existing = db.query(JobOffer).filter(JobOffer.url == url).first()
    if not existing:
        new_job = JobOffer(
            title=getattr(r, "titre", ""),
            company=getattr(r, "entreprise", ""),
            location=getattr(r, "lieu", ""),
            url=url,
            contract_type=getattr(r, "contrat", "") or getattr(r, "contract_type", ""),
            published_date=getattr(r, "date_publication", ""),
            source=source,
            status="NEW",
            original_search=search_query
        )
        db.add(new_job)
        return True
    else:
        # Mettre à jour les mots-clés de recherche
        if existing.original_search:
            if search_query.lower() not in existing.original_search.lower():
                existing.original_search += f" | {search_query}"
        else:
            existing.original_search = search_query
        return False


# ─── POST /api/scrape — Scraping intelligent avec cache ──────────────────────

@app.post("/api/scrape")
def trigger_scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    search_query = request.keyword.strip()
    if not search_query:
        return {"status": "error", "message": "Keyword required"}

    # ── Vérifier le cache : si déjà scrapé récemment, on ne re-scrape pas ──
    if is_keyword_fresh(db, search_query):
        # Compter les offres existantes pour ce mot-clé
        existing_count = db.query(JobOffer).filter(
            JobOffer.original_search.ilike(f"%{search_query}%")
        ).count()

        cache_entry = (
            db.query(ScrapeCache)
            .filter(ScrapeCache.keyword == search_query.lower())
            .first()
        )
        last_time = cache_entry.last_scraped_at if cache_entry else None

        return {
            "status": "cached",
            "message": f"Déjà scrapé récemment. {existing_count} offres en base.",
            "new_offers_count": 0,
            "total_in_db": existing_count,
            "last_scraped_at": last_time.isoformat() if last_time else None
        }

    # ── Lancer le scraping sur TOUTES les sources ──
    new_offers_count = 0
    sources_scraped = []

    # 1. Scrapers corporate (EDF, Total, Safran, Airbus)
    corporate_scrapers = [
        EDFScraper(),
        TotalEnergiesScraper(),
        SafranScraper(),
        AirbusScraper()
    ]
    for scraper in corporate_scrapers:
        try:
            print(f"\n🏭 Lancement scraper: {scraper.company_name}")
            results = scraper.scrape(keyword=search_query, max_pages=2)
            count = 0
            for r in results:
                if save_offer(db, r, r.source, search_query):
                    count += 1
            new_offers_count += count
            sources_scraped.append(f"{scraper.company_name}: {count}")
            print(f"  ✅ {scraper.company_name}: {count} nouvelles offres")
        except Exception as e:
            print(f"  ❌ Erreur {scraper.company_name}: {e}")
            sources_scraped.append(f"{scraper.company_name}: erreur")

    # 2. Indeed
    try:
        print("\n🔍 Lancement scraper: Indeed")
        from test_scraper_indeed import scrape_indeed
        indeed_results = scrape_indeed(query=search_query, location="France", max_pages=2)
        count = 0
        for r in indeed_results:
            if save_offer(db, r, "indeed", search_query):
                count += 1
        new_offers_count += count
        sources_scraped.append(f"Indeed: {count}")
        print(f"  ✅ Indeed: {count} nouvelles offres")
    except Exception as e:
        print(f"  ❌ Erreur Indeed: {e}")
        sources_scraped.append(f"Indeed: erreur")

    # 3. LinkedIn
    try:
        print("\n🔍 Lancement scraper: LinkedIn")
        from test_scraper_linkedin import scrape_linkedin
        linkedin_results = scrape_linkedin(query=search_query, location="France", max_pages=2)
        count = 0
        for r in linkedin_results:
            if save_offer(db, r, "linkedin", search_query):
                count += 1
        new_offers_count += count
        sources_scraped.append(f"LinkedIn: {count}")
        print(f"  ✅ LinkedIn: {count} nouvelles offres")
    except Exception as e:
        print(f"  ❌ Erreur LinkedIn: {e}")
        sources_scraped.append(f"LinkedIn: erreur")

    # ── Mettre à jour le cache ──
    update_cache(db, search_query, "all", new_offers_count)
    db.commit()

    return {
        "status": "success",
        "new_offers_count": new_offers_count,
        "sources": sources_scraped
    }
