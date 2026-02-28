"""
🔍 Job Hunter OS — Test Scraper Indeed (Playwright)
===================================================
Script de test pour scraper des offres d'emploi sur Indeed.fr
Utilise Playwright en mode headless pour naviguer comme un vrai navigateur.

Usage:
    python3 test_scraper_indeed.py
    python3 test_scraper_indeed.py --query "développeur python" --location "Paris"
    python3 test_scraper_indeed.py --query "data analyst" --location "Lyon" --pages 3
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
BASE_URL = "https://fr.indeed.com"

# Délais aléatoires pour simuler un humain (en secondes)
MIN_DELAY = 2
MAX_DELAY = 5


# ─── Modèle de données ───────────────────────────────────────────────────────

@dataclass
class JobOffer:
    """Représente une offre d'emploi extraite d'Indeed."""
    titre: str
    entreprise: str
    lieu: str
    url: str
    description_courte: str
    date_scraping: str
    source: str = "indeed"


# ─── Fonctions utilitaires ────────────────────────────────────────────────────

def human_delay():
    """Attend un délai aléatoire pour imiter un humain."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"  ⏳ Pause de {delay:.1f}s...")
    time.sleep(delay)


def build_search_url(query: str, location: str, start: int = 0) -> str:
    """Construit l'URL de recherche Indeed."""
    from urllib.parse import quote_plus
    url = f"{BASE_URL}/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
    if start > 0:
        url += f"&start={start}"
    return url


# ─── Scraper principal ───────────────────────────────────────────────────────

def scrape_indeed(query: str, location: str, max_pages: int = 1) -> list[JobOffer]:
    """
    Scrape les offres d'emploi depuis Indeed.fr avec Playwright.

    Args:
        query: Mots-clés de recherche (ex: "développeur python")
        location: Ville ou région (ex: "Paris")
        max_pages: Nombre de pages de résultats à scraper

    Returns:
        Liste d'objets JobOffer
    """
    all_offers: list[JobOffer] = []

    print(f"\n{'='*60}")
    print(f"🔍 Recherche Indeed : '{query}' à '{location}'")
    print(f"   Pages à scraper : {max_pages}")
    print(f"{'='*60}\n")

    with sync_playwright() as p:
        # Lancer le navigateur en mode headless (invisible)
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )

        # Créer un contexte avec un User-Agent réaliste
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
        )

        page = context.new_page()

        # Bloquer les ressources inutiles pour aller plus vite
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())
        page.route("**/analytics**", lambda route: route.abort())
        page.route("**/tracking**", lambda route: route.abort())

        for page_num in range(max_pages):
            start = page_num * 10
            url = build_search_url(query, location, start)

            print(f"📄 Page {page_num + 1}/{max_pages} — {url}")

            try:
                # Naviguer vers la page de résultats
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                human_delay()

                # Gérer le popup de cookies s'il apparaît
                try:
                    cookie_btn = page.locator(
                        "button#onetrust-accept-btn-handler, "
                        "button[aria-label='Accepter'], "
                        "button:has-text('Tout accepter'), "
                        "button:has-text('Accepter')"
                    )
                    if cookie_btn.count() > 0:
                        cookie_btn.first.click(timeout=3000)
                        print("  🍪 Popup cookies fermé")
                        time.sleep(1)
                except Exception:
                    pass  # Pas de popup, on continue

                # Chercher les cartes d'offres d'emploi
                # Indeed utilise plusieurs sélecteurs possibles selon la version du site
                job_cards = page.locator(
                    "div.job_seen_beacon, "
                    "div.jobsearch-ResultsList > div, "
                    "li.css-5lfssm, "
                    "div[data-jk], "
                    "td.resultContent"
                )

                count = job_cards.count()
                print(f"  📋 {count} offres trouvées sur cette page")

                if count == 0:
                    # Sauvegarder le HTML pour debug
                    debug_html = page.content()
                    debug_path = f"debug_indeed_page_{page_num + 1}.html"
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(debug_html)
                    print(f"  ⚠️  Aucune offre trouvée ! HTML sauvegardé dans {debug_path}")
                    print(f"  💡 Le site a peut-être détecté le scraping ou la structure a changé.")

                    # Vérifier si on est bloqué
                    if "captcha" in debug_html.lower() or "blocked" in debug_html.lower():
                        print("  🚫 CAPTCHA ou blocage détecté ! Arrêt du scraping.")
                        break
                    continue

                # Extraire les données de chaque offre
                for i in range(count):
                    try:
                        card = job_cards.nth(i)

                        # Titre du poste
                        title_el = card.locator(
                            "h2.jobTitle a, "
                            "a[data-jk], "
                            "span[id^='jobTitle'], "
                            "h2 a"
                        )
                        titre = title_el.first.inner_text(timeout=2000).strip() if title_el.count() > 0 else "N/A"

                        # Lien de l'offre
                        link_el = card.locator("h2 a, a[data-jk], a.jcs-JobTitle")
                        href = ""
                        if link_el.count() > 0:
                            href = link_el.first.get_attribute("href") or ""
                            if href.startswith("/"):
                                href = BASE_URL + href

                        # Entreprise
                        company_el = card.locator(
                            "span[data-testid='company-name'], "
                            "span.css-1h7lukg, "
                            "span.companyName, "
                            "a[data-tn-element='companyName']"
                        )
                        entreprise = company_el.first.inner_text(timeout=2000).strip() if company_el.count() > 0 else "N/A"

                        # Lieu
                        location_el = card.locator(
                            "div[data-testid='text-location'], "
                            "div.css-1restlb, "
                            "div.companyLocation"
                        )
                        lieu = location_el.first.inner_text(timeout=2000).strip() if location_el.count() > 0 else "N/A"

                        # Description courte
                        desc_el = card.locator(
                            "div.css-9446fg, "
                            "div.job-snippet, "
                            "ul[style] li, "
                            "table.jobCardShelfContainer"
                        )
                        description = ""
                        if desc_el.count() > 0:
                            description = desc_el.first.inner_text(timeout=2000).strip()[:200]

                        offer = JobOffer(
                            titre=titre,
                            entreprise=entreprise,
                            lieu=lieu,
                            url=href,
                            description_courte=description,
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
                human_delay()

        browser.close()

    # Dédoublonner par URL (Indeed affiche parfois le même job dans 2 containers)
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

def save_to_csv(offers: list[JobOffer], filename: str = "resultats_indeed.csv"):
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


def save_to_json(offers: list[JobOffer], filename: str = "resultats_indeed.json"):
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

    # Stats par entreprise
    companies: dict[str, int] = {}
    for o in offers:
        companies[o.entreprise] = companies.get(o.entreprise, 0) + 1

    print(f"\n  🏢 Entreprises uniques : {len(companies)}")
    print(f"  📍 Lieux uniques : {len(set(o.lieu for o in offers))}")

    print(f"\n  Top entreprises :")
    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    • {company} ({count} offre{'s' if count > 1 else ''})")

    # Aperçu des premières offres
    print(f"\n  📋 Aperçu (5 premières) :")
    for i, o in enumerate(offers[:5], 1):
        print(f"    {i}. {o.titre}")
        print(f"       {o.entreprise} — {o.lieu}")
        if o.description_courte:
            print(f"       {o.description_courte[:80]}...")
        print()


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🔍 Scraper Indeed.fr — Test Job Hunter OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python3 test_scraper_indeed.py
  python3 test_scraper_indeed.py --query "data analyst" --location "Lyon"
  python3 test_scraper_indeed.py --query "chef de projet" --location "Marseille" --pages 3
        """
    )
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY,
                        help=f"Mots-clés de recherche (défaut: '{DEFAULT_QUERY}')")
    parser.add_argument("--location", "-l", default=DEFAULT_LOCATION,
                        help=f"Ville ou région (défaut: '{DEFAULT_LOCATION}')")
    parser.add_argument("--pages", "-p", type=int, default=DEFAULT_PAGES,
                        help=f"Nombre de pages à scraper (défaut: {DEFAULT_PAGES})")

    args = parser.parse_args()

    # Lancer le scraping
    offers = scrape_indeed(
        query=args.query,
        location=args.location,
        max_pages=args.pages,
    )

    # Afficher le résumé
    print_summary(offers)

    # Sauvegarder les résultats
    if offers:
        save_to_csv(offers)
        save_to_json(offers)
        print("\n✅ Test terminé avec succès !")
    else:
        print("\n⚠️  Aucune offre récupérée.")
        print("   Causes possibles :")
        print("   • Indeed a détecté le scraping (CAPTCHA)")
        print("   • La structure HTML a changé")
        print("   • Problème de connexion réseau")
        print("   💡 Vérifie le fichier debug_indeed_page_1.html pour diagnostiquer")


if __name__ == "__main__":
    main()
