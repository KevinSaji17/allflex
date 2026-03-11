# Deploying AllFlex to Render - Step-by-Step Guide

This guide will walk you through deploying your Django AllFlex application to Render.

## Prerequisites

- ✅ GitHub account with your AllFlex repository pushed
- ✅ Render account (free tier available at https://render.com)
- ✅ MongoDB Atlas database (already configured)

## Step 1: Commit and Push the New Files to GitHub

First, ensure all the deployment files are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

**Files that were added/updated:**
- `build.sh` - Build script for Render
- `render.yaml` - Render configuration file
- `requirements.txt` - Updated with `gunicorn` and `whitenoise`
- `allflex/settings.py` - Updated with production settings

## Step 2: Create a New Web Service on Render

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click the "New +" button
   - Select **"Web Service"**

3. **Connect Your Repository**
   - Render will ask to connect to GitHub
   - Click "Configure account" if needed
   - Search for and select your **allflex** repository

## Step 3: Configure Your Web Service

Fill in the following settings:

### Basic Settings:
- **Name**: `allflex` (or your preferred name)
- **Region**: Choose the closest region to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave blank (unless repo is in a subdirectory)

### Build Settings:
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn allflex.wsgi:application`

## Step 4: Configure Environment Variables

Click on **"Advanced"** and add the following environment variables:

### Required Environment Variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Click "Generate" | Auto-generate a secure secret key |
| `DEBUG` | `False` | Must be False in production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your actual Render URL |
| `DATABASE_MODE` | `mongodb` | Use MongoDB |
| `MONGO_DB_NAME` | `allflex_db` | From your .env file |
| `MONGO_DB_USER` | `allflex_user` | From your .env file |
| `MONGO_DB_PASSWORD` | `1Wj1avC1davQ4Vl7` | From your .env file |
| `MONGO_DB_HOST` | `allflex-cluster.3aw66c7.mongodb.net` | From your .env file |
| `GEMINI_API_KEY` | `AIzaSyDoHlNA-JM3XHeOvHiMKXVXH2TCmHziOss` | From your .env file |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app-name.onrender.com` | Replace with your actual Render URL |
| `PYTHON_VERSION` | `3.11.0` | Specify Python version |

**Important Notes:**
- Replace `your-app-name.onrender.com` with your actual Render URL (you'll see it after deployment starts)
- The `ALLOWED_HOSTS` should NOT include `https://` or `http://`, just the domain
- The `CSRF_TRUSTED_ORIGINS` SHOULD include `https://`

## Step 5: Choose Your Plan

- **Free Tier**: Good for testing (note: services sleep after inactivity)
- **Paid Tiers**: For production use with better performance

Click **"Create Web Service"** to start the deployment.

## Step 6: Monitor the Build Process

1. Render will start building your application
2. Watch the logs in the **"Logs"** tab
3. The build process will:
   - Install dependencies from `requirements.txt`
   - Collect static files
   - Run database migrations

**Expected build time:** 3-5 minutes

## Step 7: Update Your Render URL in Environment Variables

Once deployed, Render assigns you a URL like: `https://allflex-abc123.onrender.com`

1. Copy your actual Render URL
2. Go to **"Environment"** tab
3. Update these variables with your actual URL:
   - `ALLOWED_HOSTS` = `allflex-abc123.onrender.com` (NO https://)
   - `CSRF_TRUSTED_ORIGINS` = `https://allflex-abc123.onrender.com` (WITH https://)
4. Save changes (this will trigger a redeploy)

## Step 8: Test Your Deployment

1. Visit your Render URL
2. Test key features:
   - Homepage loads
   - User registration/login
   - Gym search functionality
   - Booking system
   - Admin panel

## Step 9: Configure MongoDB Atlas Network Access (if needed)

If you get MongoDB connection errors:

1. Go to MongoDB Atlas dashboard
2. Navigate to **Network Access**
3. Click **"Add IP Address"**
4. Select **"Allow access from anywhere"** (0.0.0.0/0)
   - For production, you can restrict to Render's IPs later
5. Save changes

## Troubleshooting

### Issue: Static files not loading
**Solution:** Check that `WhiteNoise` is installed and in middleware:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be here
    ...
]
```

### Issue: CSRF verification failed
**Solution:** Ensure `CSRF_TRUSTED_ORIGINS` includes your Render URL with `https://`

### Issue: MongoDB connection timeout
**Solution:** 
- Check MongoDB Atlas network access settings
- Verify connection string in environment variables
- Ensure MongoDB password is correct (check for special characters)

### Issue: Application crashes on startup
**Solution:** Check the logs in Render dashboard for detailed error messages

## Updating Your Application

When you push changes to GitHub:
1. Render automatically detects the changes
2. Triggers a new build
3. Deploys the updated version

To manually redeploy:
- Go to your service dashboard
- Click **"Manual Deploy"**
- Select the branch to deploy

## Custom Domain (Optional)

To use your own domain:
1. Go to **"Settings"** tab
2. Scroll to **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Follow the DNS configuration instructions
5. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` with your custom domain

## Useful Render Commands

Access your application shell:
```bash
# From Render dashboard -> Shell tab
python manage.py shell
```

Check migrations:
```bash
python manage.py showmigrations
```

Create superuser (if using Django admin with SQLite for sessions):
```bash
python manage.py createsuperuser
```

## Free Tier Limitations

- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month of runtime
- Limited to 512MB RAM

## Monitoring and Logs

- **Logs Tab**: Real-time application logs
- **Metrics Tab**: CPU, memory usage
- **Events Tab**: Deployment history

## Production Checklist

- [ ] `DEBUG = False` in environment variables
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `CSRF_TRUSTED_ORIGINS` configured
- [ ] MongoDB Atlas network access configured
- [ ] All environment variables from `.env` added to Render
- [ ] Test all critical features on production URL
- [ ] Monitor first deployment logs for errors

## Support

If you encounter issues:
- Check Render logs first
- Review Django error messages
- Verify all environment variables
- Check MongoDB Atlas connection status

---

**Congratulations!** 🎉 Your AllFlex application is now live on Render!
