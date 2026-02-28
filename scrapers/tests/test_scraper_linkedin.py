"""
🔍 Job Hunter OS — Test Scraper LinkedIn Jobs (Playwright)
==========================================================
Script de test pour scraper des offres d'emploi sur LinkedIn.
Utilise la page publique LinkedIn Jobs (pas besoin de login).
Playwright en mode headless pour naviguer comme un vrai navigateur.

Usage:
    python3 test_scraper_linkedin.py
    python3 test_scraper_linkedin.py --query "data analyst" --location "Lyon"
    python3 test_scraper_linkedin.py --query "développeur python" --location "Paris" --pages 3
"""

import argparse
import csv
import json
import random
import time
from datetime import datetime
from dataclasses import dataclass, asdict

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_QUERY = "développeur"
DEFAULT_LOCATION = "Paris"
DEFAULT_PAGES = 1
RESULTS_PER_PAGE = 25  # LinkedIn affiche 25 offres par page

# Délais aléatoires pour simuler un humain (en secondes)
MIN_DELAY = 3
MAX_DELAY = 6


# ─── Modèle de données ───────────────────────────────────────────────────────

@dataclass
class JobOffer:
    """Représente une offre d'emploi extraite de LinkedIn."""
    titre: str
    entreprise: str
    lieu: str
    url: str
    date_publication: str
    description_courte: str
    date_scraping: str
    source: str = "linkedin"


# ─── Fonctions utilitaires ────────────────────────────────────────────────────

def human_delay(min_s: float = MIN_DELAY, max_s: float = MAX_DELAY):
    """Attend un délai aléatoire pour imiter un humain."""
    delay = random.uniform(min_s, max_s)
    print(f"  ⏳ Pause de {delay:.1f}s...")
    time.sleep(delay)


def build_search_url(query: str, location: str, start: int = 0) -> str:
    """Construit l'URL de recherche LinkedIn Jobs (page publique)."""
    from urllib.parse import quote_plus
    url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(query)}&location={quote_plus(location)}"
    if start > 0:
        url += f"&start={start}"
    return url


# ─── Scraper principal ───────────────────────────────────────────────────────

def scrape_linkedin(query: str, location: str, max_pages: int = 1) -> list[JobOffer]:
    """
    Scrape les offres d'emploi depuis LinkedIn Jobs avec Playwright.
    Utilise la page publique (pas besoin de login).

    Args:
        query: Mots-clés de recherche (ex: "data analyst")
        location: Ville ou région (ex: "Paris")
        max_pages: Nombre de pages de résultats à scraper

    Returns:
        Liste d'objets JobOffer
    """
    all_offers: list[JobOffer] = []

    print(f"\n{'='*60}")
    print(f"🔍 Recherche LinkedIn : '{query}' à '{location}'")
    print(f"   Pages à scraper : {max_pages}")
    print(f"{'='*60}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            extra_http_headers={
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        page = context.new_page()

        # Bloquer les ressources inutiles pour aller plus vite
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())
        page.route("**/li/track**", lambda route: route.abort())
        page.route("**/analytics**", lambda route: route.abort())

        for page_num in range(max_pages):
            start = page_num * RESULTS_PER_PAGE
            url = build_search_url(query, location, start)

            print(f"📄 Page {page_num + 1}/{max_pages} — {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                human_delay()

                # Gérer le popup cookies LinkedIn
                try:
                    cookie_btn = page.locator(
                        "button[action-type='ACCEPT'], "
                        "button:has-text('Accepter'), "
                        "button:has-text('Accept'), "
                        "button.artdeco-global-alert__action"
                    )
                    if cookie_btn.count() > 0:
                        cookie_btn.first.click(timeout=3000)
                        print("  🍪 Popup cookies fermé")
                        time.sleep(1)
                except Exception:
                    pass

                # Fermer le popup "Rejoignez LinkedIn" s'il apparaît
                try:
                    dismiss_btn = page.locator(
                        "button[data-tracking-control-name='public_jobs_contextual-sign-in-modal_modal_dismiss'], "
                        "button.modal__dismiss, "
                        "icon[data-test-icon='close-medium']"
                    ).first
                    if dismiss_btn.is_visible(timeout=2000):
                        dismiss_btn.click()
                        print("  ❌ Popup login fermé")
                        time.sleep(1)
                except Exception:
                    pass

                # Scroller vers le bas pour charger toutes les offres (lazy loading)
                print("  📜 Scroll pour charger les offres...")
                for scroll_i in range(5):
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(random.uniform(0.5, 1.2))

                # Remonter en haut
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(1)

                # Chercher les cartes d'offres (LinkedIn public job search)
                job_cards = page.locator(
                    "div.base-card, "
                    "li.jobs-search-results__list-item, "
                    "div.job-search-card, "
                    "ul.jobs-search__results-list > li"
                )

                count = job_cards.count()
                print(f"  📋 {count} offres trouvées sur cette page")

                if count == 0:
                    # Sauvegarder le HTML pour debug
                    debug_html = page.content()
                    debug_path = f"debug_linkedin_page_{page_num + 1}.html"
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(debug_html)
                    print(f"  ⚠️  Aucune offre trouvée ! HTML sauvegardé dans {debug_path}")

                    if "authwall" in debug_html.lower() or "sign in" in debug_html.lower():
                        print("  🔒 LinkedIn demande un login. La page publique est peut-être bloquée.")
                    if "captcha" in debug_html.lower():
                        print("  🚫 CAPTCHA détecté ! Arrêt du scraping.")
                        break
                    continue

                # Extraire les données de chaque offre
                for i in range(count):
                    try:
                        card = job_cards.nth(i)

                        # Titre du poste
                        title_el = card.locator(
                            "h3.base-search-card__title, "
                            "a.base-card__full-link, "
                            "h3.job-search-card__title, "
                            "span.sr-only"
                        )
                        titre = ""
                        if title_el.count() > 0:
                            titre = title_el.first.inner_text(timeout=2000).strip()

                        if not titre:
                            continue

                        # Lien de l'offre
                        link_el = card.locator(
                            "a.base-card__full-link, "
                            "a[data-tracking-control-name='public_jobs_jserp-result_search-card']"
                        )
                        href = ""
                        if link_el.count() > 0:
                            href = link_el.first.get_attribute("href") or ""
                            # Nettoyer l'URL (retirer les paramètres de tracking)
                            if "?" in href:
                                href = href.split("?")[0]

                        # Entreprise
                        company_el = card.locator(
                            "h4.base-search-card__subtitle, "
                            "a.hidden-nested-link, "
                            "h4.job-search-card__company-name"
                        )
                        entreprise = company_el.first.inner_text(timeout=2000).strip() if company_el.count() > 0 else "N/A"

                        # Lieu
                        location_el = card.locator(
                            "span.job-search-card__location, "
                            "span.base-search-card__metadata"
                        )
                        lieu = location_el.first.inner_text(timeout=2000).strip() if location_el.count() > 0 else "N/A"

                        # Date de publication
                        date_el = card.locator(
                            "time, "
                            "span.job-search-card__listdate"
                        )
                        date_pub = ""
                        if date_el.count() > 0:
                            date_pub = date_el.first.get_attribute("datetime") or date_el.first.inner_text(timeout=2000).strip()

                        offer = JobOffer(
                            titre=titre,
                            entreprise=entreprise,
                            lieu=lieu,
                            url=href,
                            date_publication=date_pub,
                            description_courte="",  # Nécessiterait de cliquer sur chaque offre
                            date_scraping=datetime.now().isoformat(),
                        )
                        all_offers.append(offer)
                        print(f"  ✅ {i+1}. {titre} — {entreprise} ({lieu})")

                    except Exception as e:
                        print(f"  ⚠️  Erreur sur l'offre {i+1}: {e}")
                        continue

            except PlaywrightTimeout:
                print(f"  ⏰ Timeout sur la page {page_num + 1}, on passe à la suivante")
                continue
            except Exception as e:
                print(f"  ❌ Erreur inattendue : {e}")
                break

            # Pause entre les pages
            if page_num < max_pages - 1:
                human_delay(4, 7)

        browser.close()

    # Dédoublonner par URL
    seen_urls: set[str] = set()
    unique_offers: list[JobOffer] = []
    for offer in all_offers:
        key = offer.url or f"{offer.titre}|{offer.entreprise}"
        if key not in seen_urls:
            seen_urls.add(key)
            unique_offers.append(offer)

    if len(unique_offers) < len(all_offers):
        print(f"\n🔄 Dédoublonnage : {len(all_offers)} → {len(unique_offers)} offres uniques")

    return unique_offers


# ─── Export des résultats ─────────────────────────────────────────────────────

def save_to_csv(offers: list[JobOffer], filename: str = "resultats_linkedin.csv"):
    """Sauvegarde les offres dans un fichier CSV."""
    if not offers:
        print("\n⚠️  Aucune offre à sauvegarder.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(offers[0]).keys()))
        writer.writeheader()
        for offer in offers:
            writer.writerow(asdict(offer))

    print(f"\n💾 {len(offers)} offres sauvegardées dans '{filename}'")


def save_to_json(offers: list[JobOffer], filename: str = "resultats_linkedin.json"):
    """Sauvegarde les offres dans un fichier JSON."""
    if not offers:
        return

    data = [asdict(o) for o in offers]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 {len(offers)} offres sauvegardées dans '{filename}'")


def print_summary(offers: list[JobOffer]):
    """Affiche un résumé des offres trouvées."""
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ — {len(offers)} offres extraites")
    print(f"{'='*60}")

    if not offers:
        print("  Aucune offre trouvée.")
        return

    companies: dict[str, int] = {}
    for o in offers:
        companies[o.entreprise] = companies.get(o.entreprise, 0) + 1

    print(f"\n  🏢 Entreprises uniques : {len(companies)}")
    print(f"  📍 Lieux uniques : {len(set(o.lieu for o in offers))}")

    print(f"\n  Top entreprises :")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    • {company} ({count} offre{'s' if count > 1 else ''})")

    print(f"\n  📋 Aperçu (5 premières) :")
    for i, o in enumerate(offers[:5], 1):
        print(f"    {i}. {o.titre}")
        print(f"       {o.entreprise} — {o.lieu}")
        if o.date_publication:
            print(f"       📅 {o.date_publication}")
        print()


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🔍 Scraper LinkedIn Jobs — Test Job Hunter OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python3 test_scraper_linkedin.py
  python3 test_scraper_linkedin.py --query "data analyst" --location "Lyon"
  python3 test_scraper_linkedin.py --query "chef de projet" --location "Marseille" --pages 2
        """
    )
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY,
                        help=f"Mots-clés de recherche (défaut: '{DEFAULT_QUERY}')")
    parser.add_argument("--location", "-l", default=DEFAULT_LOCATION,
                        help=f"Ville ou région (défaut: '{DEFAULT_LOCATION}')")
    parser.add_argument("--pages", "-p", type=int, default=DEFAULT_PAGES,
                        help=f"Nombre de pages à scraper (défaut: {DEFAULT_PAGES})")

    args = parser.parse_args()

    offers = scrape_linkedin(
        query=args.query,
        location=args.location,
        max_pages=args.pages,
    )

    print_summary(offers)

    if offers:
        save_to_csv(offers)
        save_to_json(offers)
        print("\n✅ Test terminé avec succès !")
    else:
        print("\n⚠️  Aucune offre récupérée.")
        print("   Causes possibles :")
        print("   • LinkedIn bloque le scraping (authwall/CAPTCHA)")
        print("   • La structure HTML a changé")
        print("   • Problème de connexion réseau")
        print("   💡 Vérifie le fichier debug_linkedin_page_1.html pour diagnostiquer")


if __name__ == "__main__":
    main()
