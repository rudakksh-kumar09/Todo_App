# Render Deployment Fix - Gunicorn Issues

## The Issue
```
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

**Root Cause:** Render was ignoring the Procfile and using the default command `gunicorn app:app`, but there was no `app` variable accessible in the `app` module.

## What Was Fixed

### 1. Added Module-Level App Instance
Updated `app/__init__.py` to include:
```python
# Create a module-level app instance for gunicorn app:app
app = create_app()
```

This allows both `gunicorn app:app` (Render's default) and `gunicorn run:app` (our Procfile) to work.

### 2. Updated Procfile
**New:** `web: gunicorn run:app --host 0.0.0.0 --port $PORT`

### 3. Added Models Import
Updated `app/__init__.py` to explicitly import models:
```python
# Import models to register them with SQLAlchemy
from app.models import User, Todo
```

### 4. Dual Entry Points
Now supports both:
- `gunicorn app:app` (Render's default fallback)
- `gunicorn run:app` (our preferred method via Procfile)

## How to Deploy the Fix

1. **Commit and push these changes:**
   ```bash
   git add .
   git commit -m "Fix Gunicorn deployment - add module-level app instance"
   git push origin main
   ```

2. **In Render Dashboard:**
   - The app will now work with either start command
   - Render should auto-deploy successfully

## Environment Variables for Render

Make sure these are set in your Render service:
```
DATABASE_URL=postgresql://todoapp_94pz_user:u7pE8XvlllJDnqa0Q34oJEFK1iGj5pB2@dpg-d26qbqeuk2gs73car9j0-a.oregon-postgres.render.com/todoapp_94pz
SECRET_KEY=b5afe59003b0b9b32b1fcbb28e04cc060cf1a20a31c73a50d086e9054522cee2
JWT_SECRET_KEY=1fb50a80eb7f7673b0de4bd67d926cb16374a66404959023a4c902134eb58820
FLASK_ENV=production
```

## Testing After Deployment

1. Health check: `GET https://your-app.onrender.com/`
2. API info: `GET https://your-app.onrender.com/api`

The app should now deploy successfully with either gunicorn command!
