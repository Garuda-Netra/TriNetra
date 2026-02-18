# Render Deployment Guide

This guide walks you through deploying Trinetra to Render with automatic database provisioning.

## ✅ Pre-Deployment Checklist

- [x] `render.yaml` included (auto-configuration)
- [x] `Procfile` includes `release: python manage.py migrate` (auto-runs migrations)
- [x] `.env.example` created with all required variables
- [x] `requirements.txt` includes `psycopg[binary]` for PostgreSQL
- [x] `runtime.txt` locked to Python 3.11.6
- [x] Settings auto-detect `DATABASE_URL` for PostgreSQL
- [x] WhiteNoise configured for static files
- [x] `.gitignore` excludes `.env` (secrets safe)

## 🚀 Step 1: Push to GitHub

```bash
cd g:\TriNetra
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## 🌐 Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** in the dashboard

## 📋 Step 3: Deploy with render.yaml (Automatic)

### Option A: Using render.yaml (Recommended - One-Click Deploy)

1. On Render dashboard, click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Authorize GitHub and select: `Garuda-Netra/TriNetra`
4. Render will **automatically detect `render.yaml`** and:
   - Set up a Web Service with correct build/start commands
   - Create a PostgreSQL database
   - Auto-populate environment variables
   - Link database as `DATABASE_URL`

5. **Set this one variable manually:**
   - Go to **"Environment"** tab
   - Add: `SECRET_KEY` = (generate below)
   - Click **"Create Web Service"**

**Generate SECRET_KEY** (run locally):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Option B: Manual Setup (Without render.yaml)

If Render doesn't auto-detect `render.yaml`:

1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repo
3. Fill in manually:
   - **Name**: `trinetra`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn trinetra_web.wsgi --log-file -`

4. **Create PostgreSQL Database**:
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `trinetra-postgres`
   - Render auto-adds `DATABASE_URL` to Web Service environment

5. **Add Environment Variables**:
   - `SECRET_KEY` = (generate above)
   - `DEBUG` = `false`
   - `ALLOWED_HOSTS` = `trinetra-xxxxx.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://trinetra-xxxxx.onrender.com`
   - `SECURE_SSL_REDIRECT` = `true`

6. Click **"Create Web Service"**

## 📊 Step 4: Monitor Deployment

1. Watch the **"Logs"** tab for build progress (2-5 minutes)
2. Look for this in logs:
   ```
   Starting gunicorn 22.0.0
   Listening at: 0.0.0.0:10000
   ```
3. Once deployment completes, Render gives you a live URL:
   ```
   https://trinetra-xxxxx.onrender.com
   ```

## ✔️ Step 5: Verify Deployment

1. Open your Render URL in browser
2. You should see the Trinetra scanner home page
3. Try a test scan to confirm everything works

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'app'`
- **Cause**: Start Command is wrong
- **Fix**: Verify Start Command is exactly: `gunicorn trinetra_web.wsgi --log-file -`

### Error: `DisallowedHost`
- **Cause**: `ALLOWED_HOSTS` not set correctly
- **Fix**: Add your actual Render URL to `ALLOWED_HOSTS` environment variable

### Error: Database connection issues
- **Cause**: `DATABASE_URL` not set
- **Fix**: Ensure PostgreSQL database is created and `DATABASE_URL` is in environment variables
- Check: Render Dashboard → Web Service → Environment → look for `DATABASE_URL`

### Static files 404 (CSS/JS not loading)
- **Cause**: `collectstatic` didn't run or failed
- **Fix**: 
  - Check logs for `collectstatic` errors
  - Manually run in Render shell: `python manage.py collectstatic --noinput`

### Data lost after restart/redeploy
- **Cause**: Using SQLite (ephemeral storage)
- **Solution**: This is expected behavior - PostgreSQL (attached) is persistent ✅

## 🔄 Redeployment

After code changes:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render auto-redeploys on push. Watch the **"Logs"** tab.

## 🔑 Environment Variables Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `abc123...` | Django secret (generate new!) |
| `DEBUG` | `false` | Never `true` in production |
| `ALLOWED_HOSTS` | `trinetra-abc123.onrender.com` | Production domain |
| `CSRF_TRUSTED_ORIGINS` | `https://trinetra-abc123.onrender.com` | CSRF-safe domain |
| `DATABASE_URL` | (auto-set by Render) | PostgreSQL connection |
| `SECURE_SSL_REDIRECT` | `true` | Force HTTPS |

## ✨ What's Included in This Deployment

- ✅ Auto-migrating database on startup (`Procfile` release command)
- ✅ Static file serving (WhiteNoise + collectstatic)
- ✅ PostgreSQL persistence (no data loss)
- ✅ HTTPS/SSL support
- ✅ Security headers (HSTS, XFO, CSRF)
- ✅ Python 3.11.6 (stable)
- ✅ Gunicorn (production WSGI server)

## 📞 Support

If deployment fails:
1. Check **Logs** tab (most helpful)
2. Check **"Events"** tab for service restarts
3. Verify all environment variables are set
4. Try **"Manual Deploy"** button to trigger rebuild

Good luck! 🚀
