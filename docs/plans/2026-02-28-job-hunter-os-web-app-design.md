# Job Hunter OS Web App — Design Document

## 1. Vision et Objectif MVP
L'objectif est de réduire drastiquement le temps nécessaire pour envoyer des candidatures qualifiées (objectif: 10 par jour avec 100% de personnalisation). L'application permettra de traiter les offres scrappées par lot ("Batch processing"), de générer les documents (CV + LM) sur mesure à partir d'un canevas pré-établi, et de les télécharger en un clic.

## 2. Parcours Utilisateur (UX) — Approche "Builder"
L'interface sera structurée en 3 étapes clés (Option C validée) :

### Étape 1 : Sourcing & Sélection
- **Fonctionnement :** L'utilisateur lance un scraping (bouton "Scraper les nouvelles offres") ou consulte la base existante.
- **Filtre "Pertinence" MVP :** Filtre par mots-clés stricts (ex: "Ingénieur") dans le titre ou la description. 
- **Action :** Une liste de N offres s'affiche. L'utilisateur coche les 5 offres les plus intéressantes de la journée pour passer à l'étape suivante.

### Étape 2 : Génération (La "Machine")
- **Fonctionnement :** L'application utilise les modèles racines (CV Word/PDF + LM type) stockés dans le profil utilisateur.
- **Action :** Le système injecte les spécificités des 5 offres sélectionnées (Titre du poste, Entreprise, Compétences clés requises) dans les canevas. Une jauge de progression s'affiche pendant la génération.

### Étape 3 : Revue & Export
- **Fonctionnement :** Un éditeur "Canevas" s'ouvre pour chaque candidature générée.
- **Action :** L'utilisateur peut relire la LM générée, ajuster les mots-clés du CV si besoin. 
- **Finalisation :** Un bouton "Télécharger le Lot (5)" permet de récupérer tous les documents finaux (PDF) classés par dossiers d'entreprise, prêts à être envoyés. Les offres correspondantes passent au statut "Candidature préparée" dans le Kanban.

## 3. Architecture Technique (Web App)
Puisque le but est d'avoir une vraie "Web App", nous allons migrer de l'idée initiale (Streamlit, qui est très basique) vers un framework moderne et robuste, idéalement **Next.js** (React) pour le frontend, connecté à notre backend Python existant (pour les scrapers et la base SQLite).

*   **Frontend :** Next.js (App Router), Tailwind CSS (Design premium type "ui-ux-pro-max").
*   **Backend :** FastAPI (Python) pour exposer les scrapers et la base de données au frontend.
*   **Base de Données :** SQLite.
*   **Génération de documents :** Python (`python-docx`, `pdfkit`) exposée via l'API.

## 4. Prochaines Étapes Techniques (Planification)
1.  **Initialiser le Backend API :** Transformer les scripts de scraping en routes FastAPI.
2.  **Initialiser le Frontend Next.js :** Créer le socle UI avec Tailwind.
3.  **Créer le composant "Canevas" :** Gérer l'upload du CV racine et l'éditeur de texte.
4.  **Connecter l'Étape 1 :** Afficher les offres scrappées dans une interface web propre.
