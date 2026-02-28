# 📁 AllFlex File Structure Cleanup & Organization

## 🎯 Production-Ready File Structure

### Current Issues
1. **allflex2/** - Duplicate/abandoned project folder (should be removed)
2. **Mixed model locations** - Models spread across accounts, gyms, users apps
3. **Unnecessary migrations** - Migration files exist but MongoDB doesn't use them
4. **Duplicate SQLite databases** - db.sqlite3 and db_dummy.sqlite3

---

## ✅ Recommended Production Structure

```
allflex/                          # Main project root
│
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (NEVER commit!)
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
│
├── allflex/                      # Core Django project settings
│   ├── __init__.py
│   ├── settings.py              # ✅ Main settings (DB mode switching)
│   ├── urls.py                  # ✅ Root URL configuration
│   ├── wsgi.py                  # Production WSGI config
│   ├── asgi.py                  # Async server config
│   ├── context_processors.py   # ✅ Template context
│   └── gym_recommender.py       # ✅ AI recommendation logic
│
├── accounts/                     # ✅ User Authentication & Profiles
│   ├── models.py                # SQLite user model (AbstractUser)
│   ├── mongo_models.py          # ✅ FIXED: MongoDB user model (complete fields)
│   ├── auth_backends.py         # ✅ Custom MongoDB authentication backend
│   ├── forms.py                 # ✅ FIXED: Dynamic signup form
│   ├── views.py                 # ✅ Login, signup, redirect views
│   ├── urls.py                  # Account-related URLs
│   ├── db_utils.py              # ✅ Database abstraction layer
│   ├── session_serializers.py   # MongoDB session serialization
│   ├── admin.py                 # Django admin config
│   ├── templates/
│   │   └── registration/
│   │       ├── login.html       # ✅ Login page
│   │       └── signup.html      # ✅ Sign up page
│   └── management/
│       └── commands/
│           ├── create_mongo_superuser.py  # MongoDB admin creation
│           ├── test_mongo_auth.py         # Authentication testing
│           └── fix_admin_role.py          # Demo user creation
│
├── gyms/                         # ✅ Gym Management
│   ├── models.py                # SQLite: Gym, Booking, Rating, PayoutRequest
│   ├── views.py                 # Gym listing, booking, ratings
│   ├── urls.py                  # Gym-related URLs
│   ├── admin.py
│   ├── templates/
│   │   └── gyms/
│   │       ├── dashboard.html   # Gym owner dashboard
│   │       └── list.html        # Gym listing page
│   └── management/
│       └── commands/
│           └── create_credit_packs.py  # Initialize credit packs
│
├── users/                        # ✅ User Features (Credits, Bookings)
│   ├── models.py                # SQLite: CreditPack, CreditTransaction, GymBooking
│   ├── views.py                 # User dashboard, credit purchase
│   ├── urls.py                  # User-related URLs
│   ├── admin.py
│   └── templates/
│       └── users/
│           ├── dashboard.html   # User dashboard
│           ├── home.html        # Landing page
│           ├── plans.html       # Credit packages display
│           └── plans_credits.html  # Credit-based plans
│
├── adminpanel/                   # ✅ Admin Dashboard
│   ├── views.py                 # Admin overview, gym approvals, payouts
│   ├── urls.py                  # Admin panel URLs
│   ├── templates/
│   │   └── adminpanel/
│   │       ├── dashboard.html   # Admin dashboard
│   │       ├── approve_gyms.html
│   │       └── manage_payouts.html
│
├── theme/                        # ✅ Tailwind CSS & Static Files
│   ├── static/
│   │   └── css/
│   │       └── dist/
│   │           └── styles.css   # Compiled Tailwind CSS
│   ├── static_src/
│   │   ├── tailwind.config.js   # Tailwind configuration
│   │   ├── postcss.config.js
│   │   ├── package.json
│   │   └── src/
│   │       └── styles.css       # Source Tailwind styles
│   └── templates/
│       ├── base.html            # ✅ Base template (all pages extend this)
│       └── components/
│           └── navbar.html      # Reusable navbar component
│
├── staticfiles/                  # Collected static files (production)
├── media/                        # User uploads (QR codes, gym logos)
│
├── db.sqlite3                    # SQLite database (when DATABASE_MODE=sqlite)
├── db_dummy.sqlite3              # Dummy DB for contrib apps (when using MongoDB)
│
└── docs/                         # Documentation (NEW - consolidate all .md files)
    ├── MONGODB_SETUP.md          # MongoDB Atlas setup guide
    ├── MIGRATION_GUIDE.md        # Migration instructions
    ├── TESTING_GUIDE.md          # Testing procedures
    └── API_REFERENCE.md          # API documentation (future)
```

---

## 🗑️ Files & Folders to Remove

### 1. **allflex2/** - Entire folder
```bash
# REMOVE: Duplicate/abandoned project
rm -rf allflex2/
```

### 2. **Migration files** (optional, if using MongoDB exclusively)
```bash
# These are only needed for SQLite mode
# If using MongoDB exclusively in production, you can remove:
accounts/migrations/*
gyms/migrations/*
users/migrations/*
adminpanel/migrations/*

# BUT keep __init__.py in each migrations folder
```

---

## 📋 File Organization Best Practices

### **1. Models Organization**

**Current Issue:** Models scattered across multiple apps

**Production Approach:**
- **accounts/** - User authentication only
- **gyms/** - Gym-related models (Gym, Booking, Rating, PayoutRequest)
- **users/** - User-related models (CreditPack, CreditTransaction, GymBooking)

**MongoDB Consolidation:**
- All MongoDB models are in `accounts/mongo_models.py` (centralized)
- Use `db_utils.py` to abstract database access

### **2. Templates Organization**

```
theme/templates/          # Global templates (base.html, components)
accounts/templates/       # Account-specific (login, signup)
gyms/templates/           # Gym-specific pages
users/templates/          # User-specific pages
adminpanel/templates/     # Admin-specific pages
```

### **3. Static Files Organization**

```
theme/static/            # Production-ready static files
theme/static_src/        # Development source files (Tailwind)
staticfiles/             # Collected static (production, .gitignored)
media/                   # User uploads (.gitignored)
```

---

## 🔄 Migration Plan

### **Phase 1: Backup** ✅
```bash
# Create backup before changes
cp -r allflex allflex_backup_$(date +%Y%m%d)
```

### **Phase 2: Remove Duplicates** ⚠️
```bash
# Remove abandoned project
rm -rf allflex2/

# Remove unnecessary docs from root (move to docs/)
mkdir -p docs/
mv *.md docs/  # Keep README.md in root
mv README.md ./
```

### **Phase 3: Clean Database Files** ⚠️
```bash
# If using MongoDB exclusively:
# - Keep db_dummy.sqlite3 (needed for Django contrib apps)
# - Can delete db.sqlite3 (SQLite mode database)
```

### **Phase 4: Update .gitignore** ✅
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Django
*.log
db.sqlite3
db_dummy.sqlite3
media/
staticfiles/
*.pot
*.pyc
local_settings.py

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node (Tailwind)
node_modules/
package-lock.json

# Backups
*_backup_*/
*.bak
```

---

## ✅ Current Structure Status

### **Well-Organized** ✅
- ✅ `accounts/` - Clear authentication logic
- ✅ `gyms/` - Well-structured gym management
- ✅ `users/` - User features properly separated
- ✅ `adminpanel/` - Dedicated admin functionality
- ✅ `theme/` - Centralized styling with Tailwind
- ✅ `allflex/settings.py` - Clean database mode switching

### **Needs Cleanup** ⚠️
- ⚠️ `allflex2/` - Remove this folder
- ⚠️ Root directory - Too many .md files (move to docs/)
- ⚠️ Migration files - Not needed for MongoDB (optional cleanup)

### **Fixed in This Session** 🎉
- 🎉 `accounts/mongo_models.py` - Added all missing UserProfile fields
- 🎉 `accounts/forms.py` - Dynamic model selection (SQLite/MongoDB)
- 🎉 `accounts/views.py` - Proper role handling in signup

---

## 🚀 Production Deployment Checklist

### **1. Environment Configuration**
- [ ] Set `DEBUG=False` in production `.env`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with actual domain
- [ ] Set `DATABASE_MODE=mongodb` for production
- [ ] Configure MongoDB Atlas credentials

### **2. Static Files**
```bash
python manage.py collectstatic --noinput
```

### **3. Database**
- [ ] Verify MongoDB connection
- [ ] Create superuser: `python manage.py create_mongo_superuser`
- [ ] Initialize credit packs: `python manage.py create_credit_packs`

### **4. Security**
- [ ] Enable HTTPS
- [ ] Set secure cookie settings
- [ ] Configure CORS if needed
- [ ] Set up MongoDB IP whitelist (remove 0.0.0.0/0)

### **5. Server Configuration**
- [ ] Configure WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Configure domain & SSL certificate
- [ ] Set up monitoring & logging

---

## 📝 Notes

1. **Database Mode Switching:** Your app supports both SQLite and MongoDB via `DATABASE_MODE` env variable
2. **Models:** Use `db_utils.get_user_model()` etc. for database-agnostic code
3. **Authentication:** Custom backend (`MongoEngineAuthBackend`) handles MongoDB users
4. **Sessions:** Custom serializer handles MongoDB ObjectId in sessions
5. **Admin Panel:** Works with both databases (dummy SQLite used for contrib apps with MongoDB)

---

**Last Updated:** February 19, 2026
**Status:** File structure documented, critical bugs fixed ✅
