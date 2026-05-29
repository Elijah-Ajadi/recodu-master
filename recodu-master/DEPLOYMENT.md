# Recodu Deployment Guide

## Vercel + Neon PostgreSQL Setup

### 1. Push to Git
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Create Vercel Project
- Go to [vercel.com](https://vercel.com) → New Project
- Import your Git repository
- Framework Preset: **Other**

### 3. Configure Environment Variables
In Vercel Project Settings → Environment Variables, add:

| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `your-app-name.vercel.app,localhost` |
| `DATABASE_URL` | Your Neon connection string (see below) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-app-name.vercel.app` |

### 4. Get Neon Database URL
From your Neon dashboard:
1. Go to your project → Connection Details
2. Copy the **Connection string** (looks like: `postgresql://user:password@host/database`)
3. Paste as `DATABASE_URL` in Vercel env vars

### 5. Deploy
- Vercel will auto-deploy on push
- First deployment runs `build.sh` which:
  - Installs dependencies
  - Runs `collectstatic`
  - Runs database migrations

### 6. Create Superuser
After first deployment, run in Vercel CLI:
```bash
vercel env pull .env.production
vercel run python manage.py createsuperuser
```

Or use Vercel's "Storage" → "Postgres" → "Execute SQL" to create admin manually.

### Local Development
```bash
cp .env.example .env
# Edit .env with your local values
python manage.py runserver
```

### Project Structure
```
recodu/
├── recodu/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   └── production.py    # Vercel/production settings
│   ├── settings.py          # Local dev (SQLite)
│   └── wsgi.py              # Vercel entry point
├── vercel.json              # Vercel config
├── build.sh                 # Build script
├── requirements.txt         # Production deps
└── .env.example            # Env template
```
