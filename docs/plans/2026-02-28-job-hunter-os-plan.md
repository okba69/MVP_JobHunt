# Plan d'implémentation : Job Hunter OS Web App (V1)

> **Pour l'Assistant Automatisé :** Ce plan de travail décrit l'implémentation détaillée étape par étape.

**Objectif :** Créer une Web App permettant de scraper, filtrer, et générer en lot des candidatures (CV/LM) personnalisées via une interface "Builder".

**Architecture :** 
L'application utilisera FastAPI pour exposer les scrapers existants et gérer la base SQLite. Le frontend sera construit en Next.js (App Router) avec TailwindCSS pour offrir une interface utilisateur fluide, moderne et premium, permettant le traitement par lot de 5 offres à la fois.

**Stack Technique :** 
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (SQLite), python-docx (Génération de documents).
- **Frontend:** Next.js 14, React, TailwindCSS, Lucide React (Icônes).

---

### Phase 1 : Socle Backend & Base de Données

#### Tâche 1: Initialisation du projet Backend et de la Base de Données SQLite

**Fichiers :**
- Créer : `backend/requirements.txt`
- Créer : `backend/database.py`
- Créer : `backend/models.py`
- Test : `backend/tests/test_database.py`

**Étape 1 : Écrire le test qui échouera**
```python
# backend/tests/test_database.py
import pytest
from sqlalchemy import inspect
from backend.database import engine, Base
from backend.models import JobOffer

def test_database_tables_created():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    assert "job_offers" in inspector.get_table_names()
```

**Étape 2 : Lancer le test pour valider qu'il échoue**
Démarrer : `pytest backend/tests/test_database.py`
Attendu : ÉCHEC (fichiers inexistants)

**Étape 3 : Écrire l'implémentation minimale**
```text
# backend/requirements.txt
fastapi
uvicorn
sqlalchemy
pytest
python-docx
```

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///../data/job_hunter.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base
import datetime

class JobOffer(Base):
    __tablename__ = "job_offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    url = Column(String, unique=True, index=True)
    contract_type = Column(String)
    published_date = Column(String)
    status = Column(String, default="NEW") # NEW, SELECTED, APPLIED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```

**Étape 4 : Lancer le test pour valider qu'il passe**
Démarrer : `pip install -r backend/requirements.txt && pytest backend/tests/test_database.py`
Attendu : PASS

**Étape 5 : Commit**
```bash
git add backend/
git commit -m "feat(backend): init db engine and JobOffer model"
```

---

#### Tâche 2: API de Scraping et Endpoints Jobs

**Fichiers :**
- Créer : `backend/main.py`
- Modifier : `scrapers/tests/test_scraper_corporate.py` -> Déplacer la logique dans `backend/services/scraper_service.py`
- Test : `backend/tests/test_api.py`

**Étape 1 : Écrire le test qui échouera**
```python
# backend/tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_jobs_empty():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []
```

**Étape 2 : Lancer le test pour valider qu'il échoue**
Démarrer : `pytest backend/tests/test_api.py`
Attendu : ÉCHEC (main.py introuvable)

**Étape 3 : Écrire l'implémentation minimale**
```python
# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import engine, Base, get_db
from backend.models import JobOffer

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Hunter OS API")

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(JobOffer).all()
```
*(Note: L'intégration complète du scraper service sera faite dans une étape subséquente pour isoler la logique).*

**Étape 4 : Lancer le test pour valider qu'il passe**
Démarrer : `pytest backend/tests/test_api.py`
Attendu : PASS

**Étape 5 : Commit**
```bash
git add backend/main.py backend/tests/test_api.py
git commit -m "feat(backend): create get jobs endpoint"
```

---

### Phase 2 : Socle Frontend (Next.js)

#### Tâche 3: Initialisation Next.js et Layout Principal

**Fichiers :**
- Créer : Structure Next.js via `npx create-next-app`
- Modifier : `frontend/src/app/layout.tsx`
- Modifier : `frontend/src/app/page.tsx`

**Étape 1 : Initialisation**
Démarrer : `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*" --use-npm`
Attendu : Projet frontend créé.

**Étape 2 : Créer le layout "Pro Max" avec Sidebar**
```tsx
// frontend/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Job Hunter OS',
  description: 'Automated Job Application System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-50 flex h-screen overflow-hidden`}>
        {/* Sidebar placeholder */}
        <aside className="w-64 border-r border-gray-800 bg-gray-900/50 p-4">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            Job Hunter OS
          </h1>
        </aside>
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8">
          {children}
        </main>
      </body>
    </html>
  )
}
```

```tsx
// frontend/app/page.tsx
export default function Home() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Dashboard Candidatures</h2>
      <div className="grid grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-gray-900 border border-gray-800 shadow-xl">
          <h3 className="text-lg font-medium text-gray-400">Nouvelles Offres</h3>
          <p className="text-4xl font-bold mt-2">0</p>
        </div>
      </div>
    </div>
  )
}
```

**Étape 3 : Commit**
```bash
git add frontend/
git commit -m "feat(frontend): init nextjs app with dark mode layout"
```

---

### Phase 3 : Le Flux "Builder" (Sélection → Génération)

#### Tâche 4: Composant Liste des Offres (Étape 1 du Builder)

**Objectif :** Afficher les offres (mockées puis réelles), permettre la sélection via des checkboxes, et valider si 5 = sélectionnées.
*(L'implémentation complète des composants React "Builder" suivra le design Premium)*.

#### Tâche 5: Moteur de Génération de Documents (Backend)
- Utilisation de `python-docx` pour lire `templates/base_cv.docx` et `templates/base_lm.docx`.
- Remplacement dynamique de placeholders ex: `{{ENTREPRISE}}`, `{{TITRE_POSTE}}`.

---
*Fin du plan initial. Les composants spécifiques UI seront développés de manière itérative selon le besoin.*
