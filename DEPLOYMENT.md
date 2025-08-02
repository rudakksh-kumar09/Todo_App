# Render Deployment Guide

## Prerequisites
1. A Render account (https://render.com)
2. Your code pushed to a GitHub repository
3. A PostgreSQL database (Render provides this)

## Step-by-Step Deployment

### 1. Create a PostgreSQL Database on Render
1. Go to your Render dashboard
2. Click "New" → "PostgreSQL"
3. Choose a name for your database
4. Select the free tier or paid tier as needed
5. Click "Create Database"
6. Note the database URL provided

### 2. Create a Web Service on Render
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Choose the repository containing this backend code
4. Configure the service:
   - **Name**: Your app name (e.g., "todo-app-backend")
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Plan**: Free or paid tier

### 3. Set Environment Variables
In your Render web service settings, add these environment variables:

#### Required Variables:
- `DATABASE_URL`: Use the PostgreSQL database URL from step 1
- `SECRET_KEY`: Generate a strong random key (use Python: `import secrets; secrets.token_hex(32)`)
- `JWT_SECRET_KEY`: Generate another strong random key

#### Google OAuth (if using):
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

#### Email Configuration (if using):
- `MAIL_SERVER`: smtp.gmail.com
- `MAIL_PORT`: 587
- `MAIL_USERNAME`: your-email@gmail.com
- `MAIL_PASSWORD`: your-app-password (not your regular password!)
- `MAIL_USE_TLS`: True
- `MAIL_USE_SSL`: False

#### Production Settings:
- `FLASK_ENV`: production
- `CORS_ORIGINS`: Your frontend URL (e.g., https://your-frontend.onrender.com)

### 4. Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy your app
3. Monitor the build logs for any errors

### 5. Initialize Database
After successful deployment, you may need to initialize your database:
1. Go to your web service dashboard
2. Open the "Shell" tab
3. Run: `python init_db.py`

### 6. Test Your Deployment
Your API will be available at: `https://your-service-name.onrender.com`

Test endpoints:
- Health check: `GET https://your-service-name.onrender.com/`
- API info: `GET https://your-service-name.onrender.com/api`

## Important Notes

1. **Free Tier Limitations**: 
   - Services spin down after 15 minutes of inactivity
   - Cold starts may take 30+ seconds

2. **Database Security**: 
   - Never commit sensitive credentials to Git
   - Use environment variables for all secrets

3. **CORS Configuration**: 
   - Update `CORS_ORIGINS` with your actual frontend URL
   - Remove localhost URLs in production

4. **SSL/HTTPS**: 
   - Render provides HTTPS automatically
   - Update any hardcoded HTTP URLs to HTTPS

## Troubleshooting

- **Build Failures**: Check that all dependencies are in requirements.txt
- **Database Connection Issues**: Verify DATABASE_URL is correct
- **CORS Errors**: Ensure frontend URL is in CORS_ORIGINS
- **App Won't Start**: Check that Procfile and gunicorn are configured correctly

## Security Checklist

- [ ] Generated strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Removed development database credentials
- [ ] Set FLASK_ENV to "production"
- [ ] Configured proper CORS origins
- [ ] Using environment variables for all secrets
- [ ] Gmail app password configured (not regular password)
