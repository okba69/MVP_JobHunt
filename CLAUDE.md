# CLAUDE.md — Job Hunter OS · Mémoire Projet

> Ce fichier sert de mémoire persistante pour Claude Code. Il contient le contexte, les décisions techniques et les conventions du projet. **Lis ce fichier en premier à chaque session.**

---

## 🎯 Objectif du Projet

**Job Hunter OS** est un tableau de bord personnel pour centraliser et automatiser la recherche d'emploi :
- Suivre toutes les candidatures dans un pipeline visuel (Kanban)
- Scraper des offres depuis Indeed et Welcome to the Jungle
- Détecter automatiquement les réponses reçues par email (Gmail)
- Exporter les données en Excel

**Public cible** : un utilisateur unique (moi), en local.

---

## 🏗️ Stack Technique

| Composant | Technologie | Version min |
|-----------|-------------|-------------|
| Frontend | Streamlit | 1.30+ |
| Backend | Python | 3.11+ |
| Base de données | SQLite (stdlib) | — |
| Scraping | requests + BeautifulSoup4 | — |
| Emails | Gmail API (google-api-python-client) | — |
| Export | pandas + openpyxl | — |
| Graphiques | plotly | — |

---

## 📁 Structure du Projet

```
job-hunter-os/
├── CLAUDE.md              # CE FICHIER — mémoire projet
├── README.md              # Doc utilisateur
├── requirements.txt       # Dépendances
├── app.py                 # Point d'entrée Streamlit
├── config.py              # Constantes, chemins
├── database.py            # SQLite : connexion + CRUD
├── models.py              # Dataclasses
├── pages/                 # Pages Streamlit
│   ├── dashboard.py       # Kanban
│   ├── add_candidature.py # Formulaire
│   ├── search_offers.py   # Recherche offres
│   ├── emails.py          # Suivi emails
│   └── stats.py           # Statistiques
├── scrapers/              # Modules de scraping
│   ├── base.py            # Classe abstraite
│   ├── indeed.py
│   └── wttj.py
├── email_client/          # Intégration Gmail
│   ├── gmail.py
│   └── classifier.py
├── utils/
│   ├── export.py          # Export Excel/CSV
│   └── anti_block.py      # Anti-blocage (headers, délais)
├── tests/
├── data/                  # BDD SQLite (générée)
└── credentials/           # OAuth2 (gitignored)
```

---

## 🗄️ Schéma Base de Données

### Table `candidatures`
```sql
CREATE TABLE candidatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entreprise TEXT NOT NULL,
    poste TEXT NOT NULL,
    url TEXT,
    statut TEXT DEFAULT 'a_postuler',  -- a_postuler|postule|relance|entretien|offre|refus
    date_candidature DATE,
    date_relance DATE,
    notes TEXT,
    source TEXT,          -- manuel|indeed|wttj|csv
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table `offres_scrapees`
```sql
CREATE TABLE offres_scrapees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    entreprise TEXT,
    lieu TEXT,
    url TEXT UNIQUE,      -- dédoublication par URL
    source TEXT,          -- indeed|wttj
    date_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    importee BOOLEAN DEFAULT 0  -- converti en candidature ?
);
```

### Table `emails_recus`
```sql
CREATE TABLE emails_recus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gmail_id TEXT UNIQUE,
    expediteur TEXT,
    sujet TEXT,
    date_reception TIMESTAMP,
    classification TEXT,  -- positif|negatif|relance|inconnu
    candidature_id INTEGER REFERENCES candidatures(id),
    lu BOOLEAN DEFAULT 0
);
```

---

## 📐 Conventions de Code

### Style
- **Python** : PEP 8, docstrings Google-style
- **Nommage** : `snake_case` partout (fichiers, fonctions, variables)
- **Imports** : stdlib → third-party → local, séparés par ligne vide
- **Type hints** : obligatoires sur les signatures de fonctions

### Streamlit
- Chaque page = un fichier dans `pages/`
- `st.set_page_config()` uniquement dans `app.py`
- Utiliser `st.session_state` pour l'état entre les pages
- Utiliser `st.cache_data` pour les requêtes BDD

### Base de données
- Toutes les requêtes passent par `database.py`, jamais de SQL direct dans les pages
- Utiliser des paramètres `?` pour les requêtes (jamais de f-string SQL)
- Toujours fermer les connexions (context manager `with`)

### Scraping
- Hériter de `BaseScraper` dans `scrapers/base.py`
- Délai aléatoire entre requêtes : `time.sleep(random.uniform(2, 5))`
- Rotation des User-Agents via `utils/anti_block.py`
- Si erreur HTTP 403/429 → log l'erreur, ne pas crash, proposer le fallback CSV

### Gestion d'erreurs
- Try/except autour de tout appel réseau
- Messages utilisateur clairs via `st.error()` / `st.warning()`
- Logging dans un fichier `data/app.log`

---

## 🚀 Commandes Utiles

```bash
# Installation
pip install -r requirements.txt

# Lancement
streamlit run app.py

# Tests
python -m pytest tests/ -v

# Linter
python -m flake8 --max-line-length 100
```

---

## 🔑 Statuts de Candidature (Pipeline)

```
À postuler → Postulé → Relancé → Entretien → Offre reçue
                                              → Refus
```

Les statuts valides sont : `a_postuler`, `postule`, `relance`, `entretien`, `offre`, `refus`

---

## ⚠️ Points d'Attention

1. **Ne jamais commiter `credentials/`** — contient les tokens OAuth2 Gmail
2. **SQLite en mode WAL** — activer `PRAGMA journal_mode=WAL` pour la performance
3. **Scraping fragile** — les sélecteurs CSS peuvent changer → toujours tester avant un merge
4. **Gmail quota** — max ~250 requêtes/jour sur le tier gratuit, mettre un cache
5. **Pas de multi-thread** — Streamlit est single-thread, ne pas lancer de scraping lourd en synchrone → utiliser `st.spinner()` et limiter à 50 résultats

---

## 📋 Roadmap Résumée

| Phase | Contenu | Dépendances |
|-------|---------|-------------|
| 0 | Setup projet, BDD, structure | Aucune |
| 1 | Dashboard Kanban, formulaire, import/export | Phase 0 |
| 2 | Scrapers Indeed + WTTJ | Phase 0 |
| 3 | Intégration Gmail | Phase 0 + credentials Google |
| 4 | Stats, polish, tests | Phases 1-3 |
