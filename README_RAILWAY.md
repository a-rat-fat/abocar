# Turismo – Flask sur Railway (gratuit *essai*)

Ce dépôt est prêt pour **Railway** avec **Nixpacks** (pas de Dockerfile nécessaire).

## Déploiement (pas à pas)
1. Crée un nouveau repo **GitHub** et pousse ces fichiers.
2. Va sur **https://railway.com** → *New Project* → *Deploy from GitHub repo* → choisis ton repo.
3. Railway va détecter Python → installe `requirements.txt` → lance `gunicorn app:app --bind 0.0.0.0:$PORT` (via `railway.toml`).
4. À la fin du build, clique sur l’URL *Domains* pour ouvrir l’app.

### Variables / Port
- **Aucune variable obligatoire.** Railway fournit **`$PORT`** automatiquement.
- La base SQLite se crée en `data/app.db` (mais sur Railway le filesystem n’est **pas persistant**).

### ⚠️ Persistance (important)
- Le disque Railway de base **n’est pas persistant**. Pour garder tes données :
  - utilise une base gérée externe (ex : **Render Postgres (free)**), ou
  - passe sur un plan avec volume persistant, ou
  - migre plus tard vers **Supabase** ou **Neon** pour Postgres managé.
- Pour un MVP gratuit 100% : Flask (Railway) + Postgres **gratuit Render** convient très bien.

## Développement local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
gunicorn app:app --bind 127.0.0.1:8080
# http://127.0.0.1:8080
```

## Endpoints utiles
- `/api/ping` (healthcheck)
- `/demandes`, `/puits`, `/parc`, `/transports`, `/maintenance`

Bon déploiement !
