# Post-Deployment Verification Guide

After deploying to Render, use this checklist to verify everything works.

## 🔗 URLs to Test

Replace `https://your-app-name.onrender.com` with your actual Render URL.

### 1. **Home Page (Scan Interface)**
```
https://your-app-name.onrender.com/
```
**Expected**: Trinetra dashboard loads with scan form
**Check**:
- [x] Page loads without errors
- [x] CSS/styling appears (dark theme with amber/purple/cyan colors)
- [x] "Run Port Scan" form visible
- [x] No error messages or 404s

### 2. **History Page**
```
https://your-app-name.onrender.com/history/
```
**Expected**: History page with past scans (initially empty if new)
**Check**:
- [x] Page loads
- [x] Filter form visible
- [x] "◈ History" tab works

### 3. **Django Admin Panel** (Optional)
```
https://your-app-name.onrender.com/admin/
```
**Expected**: Django admin login
**Check**:
- [x] Login page appears
- [x] (Can log in with superuser if created)

## 📊 Functional Tests

### Test 1: Run a Simple Scan

1. Go to home page: `https://your-app-name.onrender.com/`
2. Enter:
   - **Target**: `localhost` or `scanme.nmap.org`
   - **Ports**: `20-30` (small range for quick test)
   - **Timeout**: `0.5`
3. Click **"Initiate Scan"**
4. **Expected Result**: Results table appears with port status

**What to watch for**:
- ❌ "ModuleNotFoundError" — Start Command is wrong (should be `gunicorn trinetra_web.wsgi --log-file -`)
- ❌ "DisallowedHost" error — `ALLOWED_HOSTS` env var not set
- ❌ Page takes forever — Port may be filtered/closed, timeout normal
- ✅ Results show (even if all closed) — Everything works!

### Test 2: Export Results

1. After a scan completes, you should see **"↓ Export CSV"** and **"↓ Export JSON"** buttons
2. Click one to download
3. **Expected**: File downloads successfully

### Test 3: Check Database

1. Go to **Render Dashboard** → Your Web Service → **"Shell"**
2. Run:
   ```bash
   python manage.py shell
   ```
3. In the Python shell:
   ```python
   from scanner.models import Scan
   print(Scan.objects.count())
   exit()
   ```
4. **Expected**: Count > 0 if scans completed

---

## 🔍 Diagnostic Checks

### Check Logs

Go to **Render Dashboard** → Your Web Service → **"Logs"** tab

**Expected** (successful startup):
```
========== Build Phase ==========
Collecting dj-database-url==2.2.0
...
Successfully installed asgiref-3.11.1 dj-database-url-2.2.0 ... whitenoise-6.8.2
Running 'pip install -r requirements.txt' complete

========== Collect Static Phase ==========
...
119 static files copied to '/opt/render/project/src/staticfiles'

========== Release Phase ==========
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...

========== Start Phase ==========
Starting gunicorn 22.0.0
Listening at: 0.0.0.0:10000
Using worker: sync
Booting worker with pid: 1234
```

**If you see errors**, common fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Wrong Start Command | Set Start Command to: `gunicorn trinetra_web.wsgi --log-file -` |
| `DisallowedHost at /` | ALLOWED_HOSTS not set | Add env var: `ALLOWED_HOSTS=your-domain.onrender.com` |
| `OperationalError: RelationalError: does not exist` | Migrations didn't run | Check Procfile has `release: python manage.py migrate` |
| `ImportError: No module named 'psycopg'` | PostgreSQL driver missing | Should work (psycopg[binary] in requirements.txt) |

### Check Environment Vars

Go to **Render Dashboard** → Your Web Service → **"Environment"** tab

**Required vars** (must exist):
```
✅ SECRET_KEY      (should be set)
✅ DEBUG           (should be "false")
✅ ALLOWED_HOSTS   (should be your domain)
✅ DATABASE_URL    (auto-set if PostgreSQL attached)
```

### Check Database Connection

1. In Render Dashboard, click your PostgreSQL instance
2. Look for **"Internal Database URL"**
3. Should be something like: `postgresql://user:pass@host:5432/db`
4. Your Web Service should have auto-linked: `DATABASE_URL=` pointing to this

---

## 🟢 All Green?

If all checks pass:

1. ✅ App is running
2. ✅ Database is persistent
3. ✅ Static files are served
4. ✅ Scans work
5. ✅ Results export
6. ✅ Ready for real use!

---

## 📱 Test on Mobile

Visit your Render URL on mobile to verify responsive design:
- Form should stack vertically
- Results table should be scrollable
- Animations should work smoothly

---

## 🚀 Next Steps

### Monitor Performance
- Watch logs for errors
- Check response times (Scans >1000 ports may be slow on free tier)
- Use Render's **"Analytics"** tab to monitor requests

### Security Hardening
- [ ] Add basic auth if not needed publicly (optional)
- [ ] Monitor for unusual scan patterns
- [ ] Keep dependencies updated (`pip install --upgrade`)

### Optional: Create Superuser for Admin
```bash
# In Render Shell
python manage.py createsuperuser
# Follow prompts
```

Then access: `https://your-domain.onrender.com/admin/`

---

## ❓ Still Having Issues?

1. **Check Render Logs** first (most helpful)
2. **Review DEPLOYMENT.md** for step-by-step setup
3. **Review RENDER_CHECKLIST.md** for what was tested
4. **Check .env.example** for env var format
5. **Verify GitHub push** includes all files (no missing dependencies)

Good luck! 🚀
