# Deployment Guide: Render & Vercel

This guide provides step-by-step instructions for deploying the AllFlex Django application to Render or Vercel.

---

## **Option 1: Deploy to Render (Recommended)**

Render is the best choice for Django applications with built-in database support and simple configuration.

### **Prerequisites**
- GitHub account
- Render account (free at [render.com](https://render.com))
- Your code pushed to a GitHub repository

### **Step-by-Step Instructions**

#### **1. Prepare Your Repository**

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/allflex.git
git branch -M main
git push -u origin main
```

#### **2. Create a Render Account**
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

#### **3. Create a New Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository (`allflex`)
3. Configure the service:

   | Field | Value |
   |-------|-------|
   | **Name** | `allflex` or any name you prefer |
   | **Region** | Choose closest to your users |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `./build.sh` |
   | **Start Command** | `gunicorn allflex.wsgi:application` |
   | **Instance Type** | `Free` (to start) |

4. Click **"Advanced"** and add environment variables:

   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.11.0` |
   | `SECRET_KEY` | Generate a secure key* |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | Your Render URL (e.g., `allflex.onrender.com`) |
   | `DATABASE_MODE` | `sqlite` or `mongodb` |
   | `GEMINI_API_KEY` | Your Google Gemini API key |

   *Generate a secure key with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

5. Click **"Create Web Service"**

#### **4. First Deployment**
- Render will automatically build and deploy your application
- Monitor the build logs for any errors
- Once deployed, your app will be available at: `https://your-app-name.onrender.com`

#### **5. Set Up Database (PostgreSQL - Recommended for Production)**

For production, use PostgreSQL instead of SQLite:

1. Create a PostgreSQL database:
   - Click **"New +"** → **"PostgreSQL"**
   - Name it `allflex-db`
   - Choose Free tier
   - Click Create

2. Update your requirements.txt to include:
   ```
   psycopg2-binary>=2.9.9
   dj-database-url>=2.1.0
   ```

3. Update `settings.py`:
   ```python
   import dj_database_url
   
   if os.getenv('DATABASE_URL'):
       DATABASES = {
           'default': dj_database_url.config(
               default=os.getenv('DATABASE_URL'),
               conn_max_age=600
           )
       }
   ```

4. In your web service, add environment variable:
   - Key: `DATABASE_URL`
   - Value: (Copy from PostgreSQL dashboard → Internal Database URL)

#### **6. Configure Allowed Hosts**
After deployment, update the `ALLOWED_HOSTS` environment variable:
- Go to your web service dashboard
- Environment → Add your Render URL
- Example: `allflex.onrender.com,www.allflex.onrender.com`

#### **7. Add Custom Domain (Optional)**
1. In your web service, go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Configure DNS records as instructed
4. Update `ALLOWED_HOSTS` to include your custom domain

---

## **Option 2: Deploy to Vercel**

Vercel is primarily designed for Next.js/frontend applications but can host Django using serverless functions. This is more complex and has limitations.

### **Limitations on Vercel**
- ⚠️ Each request runs in an isolated serverless function
- ⚠️ No persistent file storage (SQLite won't work reliably)
- ⚠️ Must use external database (MongoDB, PostgreSQL via external service)
- ⚠️ Cold starts can be slow
- ⚠️ Limited execution time (10 seconds on free tier)

### **Prerequisites**
- Vercel account (free at [vercel.com](https://vercel.com))
- MongoDB Atlas account (for database)
- Your code pushed to a GitHub repository

### **Step-by-Step Instructions**

#### **1. Configure for Serverless**

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "allflex/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb" }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "src": "/(.*)",
      "dest": "allflex/wsgi.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "allflex.settings"
  }
}
```

Create `vercel_wsgi.py` in the allflex directory:
```python
from .wsgi import application

# Vercel serverless function handler
def handler(request, context):
    return application
```

#### **2. Set Up MongoDB Atlas**
1. Create account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create database user and get connection string
4. Whitelist all IPs (0.0.0.0/0) for Vercel

#### **3. Update settings.py**
Force MongoDB mode for Vercel:
```python
# In settings.py
if os.getenv('VERCEL'):
    DATABASE_MODE = 'mongodb'
    DEBUG = False
```

#### **4. Deploy to Vercel**

Via Vercel Dashboard:
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

5. Add Environment Variables:
   ```
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=.vercel.app
   DATABASE_MODE=mongodb
   MONGO_DB_NAME=allflex_db
   MONGO_DB_USER=<your-mongo-user>
   MONGO_DB_PASSWORD=<your-mongo-password>
   MONGO_DB_HOST=<your-cluster>.mongodb.net
   GEMINI_API_KEY=<your-api-key>
   VERCEL=1
   ```

6. Click **"Deploy"**

Via Vercel CLI:
```bash
npm install -g vercel
vercel login
vercel --prod
```

#### **5. Limitations to Consider**
- Static files must be served via CDN (use WhiteNoise or external CDN)
- No background tasks or scheduled jobs
- Each request is isolated (no WebSockets)
- User uploads must use external storage (S3, Cloudinary)

---

## **Recommendation**

### **Use Render if:**
- ✅ You want simple deployment
- ✅ You need background workers
- ✅ You want to use PostgreSQL
- ✅ You need longer execution times
- ✅ This is your first deployment

### **Use Vercel if:**
- You're already using Vercel for frontend
- You need global edge deployment
- You're comfortable with serverless limitations
- You have external database and storage

---

## **Post-Deployment Checklist**

### **Security**
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` correctly
- [ ] Enable HTTPS (automatic on both platforms)
- [ ] Set `CSRF_TRUSTED_ORIGINS`

### **Database**
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Set up database backups

### **Static Files**
- [ ] Run `collectstatic`: `python manage.py collectstatic`
- [ ] Verify CSS/JS loads correctly
- [ ] Test image uploads (if using media files)

### **Environment Variables**
- [ ] All API keys configured
- [ ] Email settings configured
- [ ] MongoDB credentials (if using)

### **Testing**
- [ ] Test user registration/login
- [ ] Test gym booking flow
- [ ] Test admin panel access
- [ ] Check mobile responsiveness
- [ ] Monitor error logs

---

## **Troubleshooting**

### **Build Failures**
```bash
# Check build.sh has executable permissions
chmod +x build.sh

# Test locally
./build.sh
```

### **Static Files Not Loading**
- Ensure `collectstatic` runs in build command
- Verify `STATIC_ROOT` is set correctly
- Check WhiteNoise is installed and configured

### **Database Connection Errors**
- Verify environment variables are set
- Check database credentials
- For MongoDB: Ensure IP whitelist includes Render/Vercel IPs

### **Application Errors**
- Check logs in Render/Vercel dashboard
- Set `DEBUG=True` temporarily to see detailed errors
- Verify all dependencies are in requirements.txt

---

## **Useful Commands**

```bash
# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Test production settings locally
DEBUG=False python manage.py runserver

# Collect static files locally
python manage.py collectstatic --no-input

# Check for deployment issues
python manage.py check --deploy
```

---

## **Cost Estimates**

### **Render Free Tier**
- 750 hours/month free
- Sleeps after 15 minutes of inactivity
- 512 MB RAM, shared CPU
- **Upgrade to Starter ($7/month)**: No sleep, more resources

### **Vercel Free Tier**
- 100 GB bandwidth/month
- Serverless function invocations included
- 10 second execution limit
- **Upgrade to Pro ($20/month)**: More bandwidth, longer execution

---

## **Next Steps**

1. Choose your platform (Render recommended)
2. Push your code to GitHub
3. Follow the deployment steps
4. Configure environment variables
5. Test your deployed application
6. Set up monitoring and backups

For questions or issues, refer to:
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
