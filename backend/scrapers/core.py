"""
🏭 Job Hunter OS — Scraper Sites Carrières Entreprises (Playwright)
====================================================================
Script modulaire pour scraper les offres d'emploi directement sur les
sites carrières des grandes entreprises industrielles françaises.

Architecture :
    - BaseCorporateScraper : classe abstraite réutilisable
    - EDFScraper : implémentation pour EDF Recrute
    - COMPANIES_REGISTRY : dictionnaire des entreprises et leurs URLs

Pour ajouter une nouvelle entreprise, il suffit de :
    1. Créer une classe qui hérite de BaseCorporateScraper
    2. Implémenter les méthodes extract_job_cards() et parse_card()
    3. L'ajouter au COMPANIES_REGISTRY

Usage:
    python3 test_scraper_corporate.py
    python3 test_scraper_corporate.py --company edf --keyword "ingénieur"
    python3 test_scraper_corporate.py --company edf --keyword "data" --pages 3
    python3 test_scraper_corporate.py --list   # Lister les entreprises disponibles
"""

import argparse
import csv
import json
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, asdict, field

from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeout


# ─── Modèle de données ───────────────────────────────────────────────────────

@dataclass
class JobOffer:
    """Représente une offre d'emploi extraite d'un site carrière."""
    titre: str
    entreprise: str
    lieu: str
    url: str
    contrat: str          # CDI, CDD, Stage, Alternance...
    date_publication: str
    description_courte: str
    source: str           # Nom du site (edf, totalenergies, etc.)
    date_scraping: str = field(default_factory=lambda: datetime.now().isoformat())


# ─── Registre des entreprises ────────────────────────────────────────────────

COMPANIES_REGISTRY: dict[str, dict] = {
    "edf": {
        "name": "EDF",
        "career_url": "https://www.edf.fr/edf-recrute/rejoignez-nous/voir-les-offres/nos-offres",
        "scraper_class": "EDFScraper",
        "sector": "Énergie",
    },
    # ── Prêts à être implémentés ─────────────────────────────────────────
    "totalenergies": {
        "name": "TotalEnergies",
        "career_url": "https://jobs.totalenergies.com/fr_FR/careers/SearchJobs",
        "scraper_class": "TotalEnergiesScraper",
        "sector": "Énergie / Pétrole",
    },
    "engie": {
        "name": "Engie",
        "career_url": "https://jobs.engie.com/search/",
        "scraper_class": None,
        "sector": "Énergie",
    },
    "safran": {
        "name": "Safran",
        "career_url": "https://www.safran-group.com/fr/offres",
        "scraper_class": "SafranScraper",
        "sector": "Aéronautique / Défense",
    },
    "thales": {
        "name": "Thales",
        "career_url": "https://careers.thalesgroup.com/fr/recherche-emploi",
        "scraper_class": None,
        "sector": "Défense / Technologie",
    },
    "airbus": {
        "name": "Airbus",
        "career_url": "https://ag.wd3.myworkdayjobs.com/fr-FR/Airbus",
        "scraper_class": "AirbusScraper",
        "sector": "Aéronautique",
    },
    "sanofi": {
        "name": "Sanofi",
        "career_url": "https://www.sanofi.com/fr/carrieres/trouver-un-emploi",
        "scraper_class": None,
        "sector": "Pharmaceutique",
    },
    "schneider": {
        "name": "Schneider Electric",
        "career_url": "https://careers.se.com/global/en/search-results",
        "scraper_class": None,
        "sector": "Électrique / Automatisation",
    },
    "saint-gobain": {
        "name": "Saint-Gobain",
        "career_url": "https://jobs.saint-gobain.com/fr/offres-d-emploi",
        "scraper_class": None,
        "sector": "Matériaux",
    },
    "michelin": {
        "name": "Michelin",
        "career_url": "https://careers.michelin.com/search/",
        "scraper_class": None,
        "sector": "Automobile / Pneumatiques",
    },
    "renault": {
        "name": "Renault Group",
        "career_url": "https://www.renaultgroup.com/talents/nos-offres/",
        "scraper_class": None,
        "sector": "Automobile",
    },
    "stellantis": {
        "name": "Stellantis",
        "career_url": "https://careers.stellantis.com/",
        "scraper_class": None,
        "sector": "Automobile",
    },
    "bouygues": {
        "name": "Bouygues",
        "career_url": "https://www.bouygues-construction.com/carrieres",
        "scraper_class": None,
        "sector": "BTP / Construction",
    },
    "vinci": {
        "name": "Vinci",
        "career_url": "https://www.vinci.com/talents/nos-offres",
        "scraper_class": None,
        "sector": "BTP / Concessions",
    },
    "veolia": {
        "name": "Veolia",
        "career_url": "https://www.veolia.com/fr/carrieres",
        "scraper_class": None,
        "sector": "Environnement / Eau",
    },
    "arcelormittal": {
        "name": "ArcelorMittal",
        "career_url": "https://corporate.arcelormittal.com/careers",
        "scraper_class": None,
        "sector": "Métallurgie / Acier",
    },
    "arkema": {
        "name": "Arkema",
        "career_url": "https://www.arkema.com/global/fr/careers/offres-emploi/",
        "scraper_class": None,
        "sector": "Chimie",
    },
    "air-liquide": {
        "name": "Air Liquide",
        "career_url": "https://www.airliquide.com/fr/carrieres",
        "scraper_class": None,
        "sector": "Chimie / Gaz industriels",
    },
    "dassault": {
        "name": "Dassault Aviation",
        "career_url": "https://www.dassault-aviation.com/fr/groupe/carrieres/",
        "scraper_class": None,
        "sector": "Aéronautique / Défense",
    },
    "naval-group": {
        "name": "Naval Group",
        "career_url": "https://www.naval-group.com/fr/nos-offres",
        "scraper_class": None,
        "sector": "Naval / Défense",
    },
    "orano": {
        "name": "Orano",
        "career_url": "https://www.orano.group/fr/carrieres",
        "scraper_class": None,
        "sector": "Nucléaire",
    },
    "legrand": {
        "name": "Legrand",
        "career_url": "https://www.legrandgroup.com/fr/carrieres",
        "scraper_class": None,
        "sector": "Électrique / Bâtiment",
    },
    "alstom": {
        "name": "Alstom",
        "career_url": "https://jobsearch.alstom.com/search/",
        "scraper_class": None,
        "sector": "Ferroviaire",
    },
    "framatome": {
        "name": "Framatome",
        "career_url": "https://www.edf.fr/edf-recrute/rejoignez-nous/voir-les-offres/nos-offres",
        "scraper_class": None,  # Même site qu'EDF (groupe EDF)
        "sector": "Nucléaire",
    },
}

# ─── Fonctions utilitaires ────────────────────────────────────────────────────

def human_delay(min_s: float = 2, max_s: float = 5):
    """Attend un délai aléatoire pour imiter un humain."""
    delay = random.uniform(min_s, max_s)
    print(f"  ⏳ Pause de {delay:.1f}s...")
    time.sleep(delay)


# ─── Classe abstraite — Base pour tous les scrapers ──────────────────────────

class BaseCorporateScraper(ABC):
    """
    Classe abstraite pour scraper un site carrière d'entreprise.

    Pour ajouter un nouveau site, hériter de cette classe et implémenter :
        - extract_job_cards(page) → renvoie le locator des cartes d'offres
        - parse_card(card, page_url) → extrait les données d'une carte
        - build_url(keyword, page_num) → construit l'URL de recherche
    """

    def __init__(self, company_key: str):
        info = COMPANIES_REGISTRY[company_key]
        self.company_key = company_key
        self.company_name = info["name"]
        self.base_url = info["career_url"]

    @abstractmethod
    def build_url(self, keyword: str, page_num: int) -> str:
        """Construit l'URL de recherche pour une page donnée."""
        ...

    @abstractmethod
    def extract_job_cards(self, page: Page) -> list:
        """Retourne la liste des éléments HTML contenant les offres."""
        ...

    @abstractmethod
    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """Parse une carte d'offre et retourne un JobOffer ou None."""
        ...

    def handle_popups(self, page: Page):
        """Gère les popups cookies / chatbot. À surcharger si besoin."""
        try:
            cookie_btn = page.locator(
                "button:has-text('Tout accepter'), "
                "button:has-text('Accepter'), "
                "button#onetrust-accept-btn-handler, "
                "button[aria-label='Accepter']"
            )
            if cookie_btn.count() > 0:
                cookie_btn.first.click(timeout=3000)
                print("  🍪 Popup cookies fermé")
                time.sleep(1)
        except Exception:
            pass

    def scrape(self, keyword: str = "", max_pages: int = 1) -> list[JobOffer]:
        """Lance le scraping. Méthode principale à appeler."""
        all_offers: list[JobOffer] = []

        print(f"\n{'='*60}")
        print(f"🏭 Recherche {self.company_name} : '{keyword or '(toutes offres)'}'")
        print(f"   Pages à scraper : {max_pages}")
        print(f"{'='*60}\n")

        with sync_playwright() as p:
            # Utiliser le Chrome système (meilleure compatibilité avec les WAF)
            # Fallback sur le Chromium bundlé si Chrome n'est pas installé
            try:
                browser = p.chromium.launch(
                    headless=True,
                    channel="chrome",
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                print("  🌐 Navigateur : Chrome système")
            except Exception:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ]
                )
                print("  🌐 Navigateur : Chromium bundlé")

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="fr-FR",
                extra_http_headers={
                    "Accept-Language": "fr-FR,fr;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )

            page = context.new_page()

            for page_num in range(max_pages):
                url = self.build_url(keyword, page_num)
                print(f"📄 Page {page_num + 1}/{max_pages} — {url}")

                # Retry logic (certains sites échouent au premier essai)
                loaded = False
                for attempt in range(3):
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        loaded = True
                        break
                    except Exception as e:
                        print(f"  🔄 Tentative {attempt + 1}/3 échouée : {type(e).__name__}")
                        if attempt < 2:
                            time.sleep(random.uniform(3, 6))

                if not loaded:
                    print(f"  ❌ Impossible de charger la page après 3 tentatives")
                    continue

                human_delay()

                # Gérer les popups (cookies, etc.)
                if page_num == 0:
                    self.handle_popups(page)

                # Scroll pour charger le contenu
                for _ in range(3):
                    page.evaluate("window.scrollBy(0, 600)")
                    time.sleep(random.uniform(0.3, 0.8))
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.5)

                # Extraire les cartes d'offres
                cards = self.extract_job_cards(page)
                count = len(cards) if isinstance(cards, list) else cards.count()
                print(f"  📋 {count} offres trouvées sur cette page")

                if count == 0:
                    debug_html = page.content()
                    debug_path = f"debug_{self.company_key}_page_{page_num + 1}.html"
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(debug_html)
                    print(f"  ⚠️  Aucune offre ! HTML sauvegardé dans {debug_path}")
                    if "captcha" in debug_html.lower():
                        print("  🚫 CAPTCHA détecté ! Arrêt.")
                        break
                    continue

                # Parser chaque carte
                for i in range(count):
                    try:
                        card = cards.nth(i) if hasattr(cards, 'nth') else cards[i]
                        offer = self.parse_card(card, url)
                        if offer:
                            all_offers.append(offer)
                            print(f"  ✅ {i+1}. {offer.titre} — {offer.contrat} ({offer.lieu})")
                    except Exception as e:
                        print(f"  ⚠️  Erreur offre {i+1}: {e}")
                        continue

                if page_num < max_pages - 1:
                    human_delay()

            browser.close()

        # Dédoublonnage
        seen: set[str] = set()
        unique: list[JobOffer] = []
        for o in all_offers:
            key = o.url or f"{o.titre}|{o.entreprise}"
            if key not in seen:
                seen.add(key)
                unique.append(o)

        if len(unique) < len(all_offers):
            print(f"\n🔄 Dédoublonnage : {len(all_offers)} → {len(unique)} offres uniques")

        return unique


# ─── Implémentation EDF ─────────────────────────────────────────────────────

class EDFScraper(BaseCorporateScraper):
    """Scraper pour le site EDF Recrute."""

    def __init__(self):
        super().__init__("edf")

    def build_url(self, keyword: str, page_num: int) -> str:
        from urllib.parse import quote_plus
        url = self.base_url + f"?page={page_num + 1}"
        if keyword:
            url += f"&search[keyword]={quote_plus(keyword)}"
        return url

    def handle_popups(self, page: Page):
        """EDF a un popup cookies + parfois un chatbot."""
        # Cookies
        try:
            cookie_btn = page.locator(
                "button#footer_tc_privacy_button_2, "
                "button:has-text('TOUT ACCEPTER'), "
                "button:has-text('Tout accepter'), "
                "button:has-text('Accepter')"
            )
            if cookie_btn.count() > 0:
                cookie_btn.first.click(timeout=3000)
                print("  🍪 Cookies acceptés")
                time.sleep(1)
        except Exception:
            pass

        # Chatbot "Besoin d'aide ?"
        try:
            chatbot_close = page.locator(
                "button[aria-label='Fermer'], "
                "button.close-chat, "
                "div.chatbot-close"
            )
            if chatbot_close.count() > 0:
                chatbot_close.first.click(timeout=2000)
                print("  🤖 Chatbot fermé")
        except Exception:
            pass

    def extract_job_cards(self, page: Page):
        """Les offres EDF sont dans des liens a.offer-link."""
        return page.locator("a.offer-link")

    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """Parse une carte d'offre EDF."""
        # Titre (h3 dans la carte)
        title_el = card.locator("h3")
        titre = title_el.first.inner_text(timeout=2000).strip() if title_el.count() > 0 else ""
        if not titre:
            return None

        # URL
        href = card.get_attribute("href") or ""
        if href and href.startswith("/"):
            href = "https://www.edf.fr" + href

        # Contenu textuel complet de la carte
        full_text = card.inner_text(timeout=2000)
        lines = [l.strip() for l in full_text.split("\n") if l.strip()]

        # Date (premier élément textuel, ex: "28 Février 2026")
        date_pub = ""
        for line in lines:
            if any(m in line.lower() for m in ["janvier","février","mars","avril","mai","juin",
                                                 "juillet","août","septembre","octobre","novembre","décembre"]):
                date_pub = line
                break

        # Contrat (après "Contrat :")
        contrat = ""
        for line in lines:
            if "contrat" in line.lower():
                contrat = line.split(":")[-1].strip() if ":" in line else line
                break

        # Lieu (après "Lieu :")
        lieu = ""
        for line in lines:
            if "lieu" in line.lower():
                lieu = line.split(":")[-1].strip() if ":" in line else line
                break

        # Entreprise (déduire du logo/texte — EDF, Framatome, Dalkia, etc.)
        entreprise = self.company_name
        for line in lines:
            lower = line.lower()
            if any(sub in lower for sub in ["framatome", "dalkia", "enedis", "edf"]):
                # On garde le texte tel quel
                if "framatome" in lower:
                    entreprise = "Framatome (Groupe EDF)"
                elif "dalkia" in lower:
                    entreprise = "Dalkia (Groupe EDF)"
                elif "enedis" in lower:
                    entreprise = "Enedis (Groupe EDF)"
                break

        return JobOffer(
            titre=titre,
            entreprise=entreprise,
            lieu=lieu,
            url=href,
            contrat=contrat,
            date_publication=date_pub,
            description_courte="",
            source="edf-recrute",
        )


# ─── Implémentation TotalEnergies ────────────────────────────────────────────

class TotalEnergiesScraper(BaseCorporateScraper):
    """Scraper pour le site TotalEnergies Jobs."""

    RESULTS_PER_PAGE = 20

    def __init__(self):
        super().__init__("totalenergies")

    def build_url(self, keyword: str, page_num: int) -> str:
        from urllib.parse import quote_plus
        base = self.base_url
        if keyword:
            base += f"/{quote_plus(keyword)}"
        url = base + f"?listFilterMode=1&jobRecordsPerPage={self.RESULTS_PER_PAGE}"
        if page_num > 0:
            url += f"&jobOffset={page_num * self.RESULTS_PER_PAGE}"
        return url

    def handle_popups(self, page: Page):
        """TotalEnergies a un popup cookies Avature."""
        try:
            cookie_btn = page.locator(
                "button:has-text('J\'accepte'), "
                "button:has-text('Tout accepter'), "
                "button:has-text('Accepter'), "
                "button#onetrust-accept-btn-handler"
            )
            if cookie_btn.count() > 0:
                cookie_btn.first.click(timeout=3000)
                print("  🍪 Cookies acceptés")
                time.sleep(1)
        except Exception:
            pass

    def extract_job_cards(self, page: Page):
        """Les offres TotalEnergies sont dans des div.article--result."""
        return page.locator("div.article--result")

    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """Parse une carte d'offre TotalEnergies."""
        # Titre
        title_el = card.locator("h3.article__header__text__title a.link, h3 a")
        titre = title_el.first.inner_text(timeout=2000).strip() if title_el.count() > 0 else ""
        if not titre:
            return None

        # URL
        href = ""
        if title_el.count() > 0:
            href = title_el.first.get_attribute("href") or ""
            if href and not href.startswith("http"):
                href = "https://jobs.totalenergies.com" + href

        # Métadonnées (dans les li de la subtitle)
        lieu = ""
        contrat = ""
        date_pub = ""
        entreprise = "TotalEnergies"

        # Localisation
        loc_el = card.locator("li.list-item-jobCountry, li.list-item-jobCity")
        if loc_el.count() > 0:
            lieu = loc_el.first.inner_text(timeout=2000).strip()

        # Type de contrat
        contract_el = card.locator("li.list-item-employmentType")
        if contract_el.count() > 0:
            contrat = contract_el.first.inner_text(timeout=2000).strip()

        # Date
        date_el = card.locator("li.list-item-jobCreationDate")
        if date_el.count() > 0:
            date_pub = date_el.first.inner_text(timeout=2000).strip()

        # Entité / société
        company_el = card.locator("li.list-item-jobEmployerCompany")
        if company_el.count() > 0:
            entreprise = company_el.first.inner_text(timeout=2000).strip()

        return JobOffer(
            titre=titre,
            entreprise=entreprise,
            lieu=lieu,
            url=href,
            contrat=contrat,
            date_publication=date_pub,
            description_courte="",
            source="totalenergies-jobs",
        )


# ─── Implémentation Safran ───────────────────────────────────────────────────

class SafranScraper(BaseCorporateScraper):
    """Scraper pour le site Safran."""

    def __init__(self):
        super().__init__("safran")

    def build_url(self, keyword: str, page_num: int) -> str:
        from urllib.parse import quote_plus
        # URL de base : https://www.safran-group.com/fr/offres
        # Paramètres : search=keyword, page=N (0-indexed)
        url = self.base_url
        params = []
        if keyword:
            params.append(f"search={quote_plus(keyword)}")
        if page_num > 0:
            params.append(f"page={page_num}")
        
        if params:
            url += "?" + "&".join(params)
        return url

    def handle_popups(self, page: Page):
        """Safran utilise souvent Axeptio ou un popup interne."""
        try:
            # Essayer d'accepter les cookies
            btns = [
                "button#axeptio_btn_acceptAll",
                "button:has-text('Accepter tout')",
                "button:has-text('Tout accepter')",
                ".axeptio-button-accept"
            ]
            for selector in btns:
                btn = page.locator(selector)
                if btn.count() > 0:
                    btn.first.click(timeout=3000)
                    print("  🍪 Cookies acceptés (Safran)")
                    time.sleep(1)
                    break
        except Exception:
            pass

    def extract_job_cards(self, page: Page):
        """
        D'après l'exploration, chaque offre est dans le listing.
        On va cibler les éléments qui contiennent le titre.
        """
        # On cherche les conteneurs d'offres. 
        # Souvent c'est un div qui contient l'offre entière.
        # Sinon on peut cibler tous les a.c-offer-item__title et remonter au parent si besoin,
        # ou itérer sur les titres.
        return page.locator("a.c-offer-item__title")

    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """
        Parse une carte d'offre Safran. 
        Note : l'argument 'card' ici est le lien titre d'après extract_job_cards.
        """
        try:
            # Titre
            titre = card.inner_text(timeout=2000).strip()
            if not titre:
                return None

            # URL
            href = card.get_attribute("href") or ""
            if href and not href.startswith("http"):
                href = "https://www.safran-group.com" + href

            # Métadonnées
            # D'après l'exploration :
            # date est le span juste après le titre
            # info_container est le div après le date
            
            # On utilise evaluateHandle pour naviguer dans le DOM relatif
            lieu = "France" # Défaut
            contrat = ""
            date_pub = ""
            entreprise = "Safran"

            # On essaie de récupérer le bloc d'info qui suit
            # Structure : <a class="c-offer-item__title">...</a> <span>Date</span> <div> <span>Entité</span> <span>Lieu</span> ... </div>
            
            # Utilisation de JS pour extraire les éléments frères/suivants complexes
            meta = card.evaluate("""(el) => {
                let date = "";
                let spans = [];
                let next = el.nextElementSibling;
                if (next && next.tagName === 'SPAN') {
                    date = next.innerText.strip || next.innerText;
                    next = next.nextElementSibling;
                }
                if (next && next.tagName === 'DIV') {
                    let s_els = next.querySelectorAll('span');
                    for (let s of s_els) spans.push(s.innerText.trim());
                }
                return { date, spans };
            }""")

            if meta.get("date"):
                date_pub = meta["date"].strip()
            
            spans = meta.get("spans", [])
            # Les spans contiennent dans l'ordre (si complet) :
            # 0: Entité, 1: Lieu, 2: Catégorie, 3: Contrat, 4: Domaine
            
            if len(spans) >= 1:
                entreprise = spans[0]
            if len(spans) >= 2:
                lieu = spans[1]
                
            # Pour la catégorie et le contrat, on cherche des mots-clés car l'ordre peut varier
            for s in spans:
                s_lower = s.lower()
                # Detection contrat
                if any(k in s_lower for k in ["cdi", "cdd", "stage", "alternance", "vie", "apprentissage", "professionnalisation"]):
                    contrat = s
                # Detection catégorie (on peut la stocker dans contrat si pas d'autre indication)
                elif not contrat and any(k in s_lower for k in ["cadre", "employé", "technicien"]):
                    contrat = s

            return JobOffer(
                titre=titre,
                entreprise=entreprise,
                lieu=lieu,
                url=href,
                contrat=contrat,
                date_publication=date_pub,
                description_courte="",
                source="safran-group",
            )
        except Exception as e:
            print(f"  ⚠️ Erreur parsing Safran: {e}")
            return None


# ─── Implémentation Airbus (Workday) ────────────────────────────────────────

class AirbusScraper(BaseCorporateScraper):
    """Scraper pour le site carrière Airbus (Workday)."""

    def __init__(self):
        super().__init__("airbus")

    def build_url(self, keyword: str, page_num: int) -> str:
        from urllib.parse import quote_plus
        # Workday Airbus : https://ag.wd3.myworkdayjobs.com/fr-FR/Airbus?q=keyword
        # Pour la page > 0, Workday ne change pas l'URL. 
        # On va gérer le changement de page par clic dans scrape() ou via un param optionnel si supporté.
        url = self.base_url
        if keyword:
            url += f"?q={quote_plus(keyword)}"
        return url

    def handle_popups(self, page: Page):
        """Accepter les cookies Workday."""
        try:
            # Banner Workday
            cookie_btn = page.locator("button:has-text('Accepter'), button:has-text('Accept')")
            if cookie_btn.count() > 0:
                cookie_btn.first.click(timeout=3000)
                print("  🍪 Cookies acceptés (Airbus/Workday)")
                time.sleep(1)
        except Exception:
            pass

    def extract_job_cards(self, page: Page):
        """Extraire les cartes d'offres Workday."""
        # On attend que les titres soient chargés
        try:
            page.wait_for_selector("a[data-automation-id='jobTitle']", timeout=10000)
        except:
            pass
        return page.locator("li:has(a[data-automation-id='jobTitle'])")

    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """Parse une offre Workday."""
        try:
            # Titre
            title_el = card.locator("a[data-automation-id='jobTitle']")
            titre = title_el.inner_text(timeout=2000).strip()
            
            # URL
            href = title_el.get_attribute("href") or ""
            if href and not href.startswith("http"):
                # URL relative Workday
                href = "https://ag.wd3.myworkdayjobs.com" + href

            # Lieu
            lieu = "Multi-sites"
            loc_el = card.locator("[data-automation-id='locations']")
            if loc_el.count() > 0:
                lieu = loc_el.first.inner_text(timeout=2000).split("\n")[-1].strip()
                # Nettoyage si le texte contient "locations"
                if "locations" in lieu.lower():
                    lieu = lieu.lower().replace("locations", "").strip().capitalize()

            # Date
            date_pub = ""
            date_el = card.locator("[data-automation-id='postedOn']")
            if date_el.count() > 0:
                date_pub = date_el.first.inner_text(timeout=2000).strip()

            # Entreprise / Entité
            entreprise = "Airbus"
            subtitle_el = card.locator("[data-automation-id='subtitle']")
            if subtitle_el.count() > 0:
                # Souvent le Job ID ou une info secondaire
                pass

            return JobOffer(
                titre=titre,
                entreprise=entreprise,
                lieu=lieu,
                url=href,
                contrat="CDI / Autre", # Workday listing ne montre pas toujours le contrat
                date_publication=date_pub,
                description_courte="",
                source="airbus-workday",
            )
        except Exception as e:
            print(f"  ⚠️ Erreur parsing Airbus: {e}")
            return None


# ─── Implémentation Engie (SuccessFactors) ──────────────────────────────────

class EngieScraper(BaseCorporateScraper):
    """Scraper pour le site carrière Engie."""

    RESULTS_PER_PAGE = 10

    def __init__(self):
        super().__init__("engie")

    def build_url(self, keyword: str, page_num: int) -> str:
        from urllib.parse import quote_plus
        # URL : https://jobs.engie.com/search/?q=keyword&locale=fr_FR&searchResultView=LIST
        url = self.base_url + f"?q={quote_plus(keyword)}&locale=fr_FR&searchResultView=LIST"
        if page_num > 0:
            url += f"&startrow={page_num * self.RESULTS_PER_PAGE}"
        return url

    def handle_popups(self, page: Page):
        """Engie utilise Cookiebot."""
        try:
            # Cookiebot banner
            cookie_btn = page.locator("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            if cookie_btn.count() > 0:
                cookie_btn.click(timeout=3000)
                print("  🍪 Cookies acceptés (Engie/Cookiebot)")
                time.sleep(1)
        except Exception:
            pass

    def extract_job_cards(self, page: Page):
        """Les offres Engie sont dans des li[data-testid='jobCard']."""
        try:
            page.wait_for_selector("li[data-testid='jobCard']", timeout=10000)
        except:
            pass
        return page.locator("li[data-testid='jobCard']")

    def parse_card(self, card, base_url: str) -> JobOffer | None:
        """Parse une carte d'offre Engie."""
        try:
            # Titre
            title_el = card.locator("a.jobCardTitle")
            titre = title_el.inner_text(timeout=2000).strip()
            
            # URL
            href = title_el.get_attribute("href") or ""
            if href and not href.startswith("http"):
                href = "https://jobs.engie.com" + href

            # Lieu
            lieu = "France"
            loc_el = card.locator("[data-testid='jobCardLocation']")
            if loc_el.count() > 0:
                lieu = loc_el.first.inner_text(timeout=2000).strip()

            # Métadonnées dans le footer
            # On cherche les valeurs dans les spans du footer
            entreprise = "Engie"
            contrat = ""
            date_pub = ""
            
            footer_values = card.locator("span[class*='jobCardFooterValue']")
            count = footer_values.count()
            
            # Typiquement : 0: Contrat, 1: Domaine, 2: Entité, 3: Date
            # Mais on va être prudent et chercher des mots clés ou labels
            full_text = card.inner_text(timeout=2000)
            
            if count >= 1:
                contrat = footer_values.nth(0).inner_text().strip()
            if count >= 3:
                entreprise = footer_values.nth(2).inner_text().strip()
            if count >= 4:
                date_pub = footer_values.nth(3).inner_text().strip()
                
            # Fallback date si le label est présent
            if "Publié le" in full_text:
                import re
                match = re.search(r"Publié le\s+(\d{2}/\d{2}/\d{4})", full_text)
                if match:
                    date_pub = match.group(1)

            return JobOffer(
                titre=titre,
                entreprise=entreprise,
                lieu=lieu,
                url=href,
                contrat=contrat,
                date_publication=date_pub,
                description_courte="",
                source="engie-jobs",
            )
        except Exception as e:
            print(f"  ⚠️ Erreur parsing Engie: {e}")
            return None


# ─── Registre des scrapers instanciables ─────────────────────────────────────

SCRAPER_CLASSES: dict[str, type[BaseCorporateScraper]] = {
    "edf": EDFScraper,
    "totalenergies": TotalEnergiesScraper,
    "safran": SafranScraper,
    "airbus": AirbusScraper,
    "engie": EngieScraper,
}


def get_scraper(company_key: str) -> BaseCorporateScraper:
    """Retourne une instance du scraper pour l'entreprise donnée."""
    if company_key not in COMPANIES_REGISTRY:
        raise ValueError(f"Entreprise '{company_key}' inconnue. Utilisez --list pour voir les disponibles.")

    if company_key not in SCRAPER_CLASSES:
        info = COMPANIES_REGISTRY[company_key]
        raise NotImplementedError(
            f"Le scraper pour {info['name']} n'est pas encore implémenté.\n"
            f"   URL carrière : {info['career_url']}\n"
            f"   Pour l'ajouter : créer une classe héritant de BaseCorporateScraper"
        )

    return SCRAPER_CLASSES[company_key]()


# ─── Export des résultats ─────────────────────────────────────────────────────

def save_to_csv(offers: list[JobOffer], filename: str):
    if not offers:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(offers[0]).keys()))
        writer.writeheader()
        for o in offers:
            writer.writerow(asdict(o))
    print(f"\n💾 {len(offers)} offres → '{filename}'")


def save_to_json(offers: list[JobOffer], filename: str):
    if not offers:
        return
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([asdict(o) for o in offers], f, ensure_ascii=False, indent=2)
    print(f"💾 {len(offers)} offres → '{filename}'")


def print_summary(offers: list[JobOffer], company_name: str):
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ {company_name} — {len(offers)} offres extraites")
    print(f"{'='*60}")

    if not offers:
        print("  Aucune offre trouvée.")
        return

    # Stats par type de contrat
    contrats: dict[str, int] = {}
    for o in offers:
        c = o.contrat or "Non précisé"
        contrats[c] = contrats.get(c, 0) + 1

    lieux: dict[str, int] = {}
    for o in offers:
        l = o.lieu or "Non précisé"
        lieux[l] = lieux.get(l, 0) + 1

    print(f"\n  📝 Types de contrat :")
    for contrat, count in sorted(contrats.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {contrat} ({count})")

    print(f"\n  📍 Top lieux :")
    for lieu, count in sorted(lieux.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"    • {lieu} ({count})")

    print(f"\n  📋 Aperçu (5 premières) :")
    for i, o in enumerate(offers[:5], 1):
        print(f"    {i}. {o.titre}")
        print(f"       {o.entreprise} — {o.contrat} — {o.lieu}")
        if o.date_publication:
            print(f"       📅 {o.date_publication}")
        print()


def list_companies():
    """Affiche la liste des entreprises disponibles."""
    print(f"\n{'='*60}")
    print(f"🏭 Entreprises industrielles françaises ({len(COMPANIES_REGISTRY)})")
    print(f"{'='*60}\n")

    for key, info in sorted(COMPANIES_REGISTRY.items()):
        status = "✅ Prêt" if key in SCRAPER_CLASSES else "⏳ À implémenter"
        print(f"  {status}  {info['name']:25s} ({info['sector']})")
        print(f"          clé: {key}")
        print(f"          {info['career_url']}")
        print()


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🏭 Scraper Sites Carrières — Grandes Entreprises Françaises",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python3 test_scraper_corporate.py --list
  python3 test_scraper_corporate.py --company edf
  python3 test_scraper_corporate.py --company edf --keyword "ingénieur" --pages 2
        """
    )
    parser.add_argument("--company", "-c", default="edf",
                        help="Clé de l'entreprise (défaut: edf)")
    parser.add_argument("--keyword", "-k", default="",
                        help="Mots-clés de recherche")
    parser.add_argument("--pages", "-p", type=int, default=2,
                        help="Nombre de pages à scraper (défaut: 2)")
    parser.add_argument("--list", action="store_true",
                        help="Lister les entreprises disponibles")

    args = parser.parse_args()

    if args.list:
        list_companies()
        return

    scraper = get_scraper(args.company)

    offers = scraper.scrape(
        keyword=args.keyword,
        max_pages=args.pages,
    )

    company_name = COMPANIES_REGISTRY[args.company]["name"]
    print_summary(offers, company_name)

    if offers:
        save_to_csv(offers, f"resultats_{args.company}.csv")
        save_to_json(offers, f"resultats_{args.company}.json")
        print(f"\n✅ Test {company_name} terminé avec succès !")
    else:
        print(f"\n⚠️  Aucune offre récupérée pour {company_name}.")
        print(f"   💡 Vérifie le fichier debug_{args.company}_page_1.html")


if __name__ == "__main__":
    main()
