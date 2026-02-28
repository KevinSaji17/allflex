# MongoDB Migration Guide for AllFlex

## ✅ Complete Step-by-Step Migration Process

### Prerequisites Checklist

- [x] MongoDB Atlas account created
- [x] Cluster created (e.g., `allflex-cluster`)
- [x] Database user created: `allflex_user`
- [x] Password set: `1Wj1avC1davQ4Vl7`
- [ ] **Cluster host URL obtained** (e.g., `allflex-cluster.xxxxx.mongodb.net`)
- [ ] Network access configured (IP whitelist)
- [ ] Python packages installed

---

## Step 1: Get Your MongoDB Atlas Cluster URL

1. **Go to MongoDB Atlas**: [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. **Navigate to**: Databases → Your Cluster → **Connect**
3. **Choose**: Drivers
4. **Copy the connection string** that looks like:
   ```
   mongodb+srv://allflex_user:<password>@allflex-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Extract the host part**: `allflex-cluster.xxxxx.mongodb.net`
   - The `xxxxx` is unique to your cluster

---

## Step 2: Update .env File

Open `c:\Users\Benedict Moncy\Documents\Projects\Saji Project\allflex\.env` and replace the `MONGO_DB_HOST` line with your actual cluster URL:

```env
# MongoDB Configuration
MONGO_DB_NAME=allflex_db
MONGO_DB_USER=allflex_user
MONGO_DB_PASSWORD=1Wj1avC1davQ4Vl7
MONGO_DB_HOST=allflex-cluster.xxxxx.mongodb.net  # ← REPLACE THIS with your actual cluster URL
```

**Example:**
```env
MONGO_DB_HOST=allflex-cluster.abc123.mongodb.net
```

The full connection string will be automatically built as:
```
mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@allflex-cluster.xxxxx.mongodb.net/allflex_db?retryWrites=true&w=majority&appName=AllFlex
```

---

## Step 3: Install Required Packages

Open PowerShell in your project directory:

```powershell
# Navigate to project directory
cd "c:\Users\Benedict Moncy\Documents\Projects\Saji Project\allflex"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install MongoDB packages
pip install -r requirements.txt
```

**Packages installed:**
- `mongoengine>=0.28.0` - MongoDB ODM for Django
- `pymongo>=4.6.0` - MongoDB Python driver
- `dnspython>=2.4.0` - DNS resolver for MongoDB Atlas SRV records

---

## Step 4: Setup MongoDB Collections & Indexes

Run the setup command:

```powershell
python manage.py setup_mongodb
```

**What this does:**
- ✅ Connects to MongoDB Atlas
- ✅ Creates collections (users, gyms, bookings, etc.)
- ✅ Creates indexes for performance
- ✅ Validates connection
- ✅ Lists all collections

**Expected output:**
```
============================================================
MongoDB Setup Starting...
============================================================

📦 Setting up: users
✅ Indexes created for users

📦 Setting up: gyms
✅ Indexes created for gyms

... (more collections)

🔍 Testing MongoDB connection...
✅ Connected to database: allflex_db
📊 Collections: users, gyms, bookings, credit_transactions, ...

============================================================
✅ MongoDB Setup Complete!
============================================================
```

---

## Step 5: Create Admin User

Create a superuser to access the admin panel:

```powershell
python manage.py create_mongo_superuser
```

**Interactive prompts:**
```
Username: admin
Email: admin@allflex.com
Password: ********
Password (again): ********

✅ Superuser "admin" created successfully!
📧 Email: admin@allflex.com
👤 Role: admin
💳 Credits: 1000
```

---

## Step 6: Test Authentication System

Verify MongoDB authentication is working:

```powershell
python manage.py test_mongo_auth
```

**This will:**
- Show all users in the database
- Let you test login with username/password
- Display user details if authentication succeeds

**Example output:**
```
============================================================
MongoDB Authentication Test
============================================================

📊 Total users in database: 1

Users:
✅ admin (admin@allflex.com) - Role: admin

------------------------------------------------------------
Test Login (or press Ctrl+C to skip)
------------------------------------------------------------

Username: admin
Password: ********

============================================================
✅ Authentication Successful!
============================================================
👤 Username: admin
📧 Email: admin@allflex.com
🎭 Role: admin
💳 Credits: 1000
📅 Date Joined: 2026-02-17 ...
🔑 User ID (MongoDB ObjectId): 65d1234567890abcdef12345
✅ Is Active: True
👔 Is Staff: True
⭐ Is Superuser: True

🎉 MongoDB authentication is working correctly!
```

---

## Step 7: Run Development Server

Start the Django development server:

```powershell
python manage.py runserver
```

**Access your application:**
- **Home**: http://127.0.0.1:8000/
- **Signup**: http://127.0.0.1:8000/accounts/signup/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Dashboard**: http://127.0.0.1:8000/dashboard/

---

## Step 8: Test Signup Flow

1. **Go to**: http://127.0.0.1:8000/accounts/signup/
2. **Fill in the form:**
   - Username: testuser
   - Email: test@example.com
   - Password: TestPass123
3. **Click**: Sign Up
4. **Expected**:
   - ✅ User created in MongoDB
   - ✅ 25 demo credits awarded
   - ✅ Redirect to login page

---

## Step 9: Verify Data in MongoDB Atlas

1. **Go to MongoDB Atlas**: [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. **Navigate to**: Databases → Browse Collections
3. **Select database**: `allflex_db`
4. **Select collection**: `users`
5. **You should see**:
   - Your admin user
   - The testuser you just created
   - All user fields (username, email, hashed password, credits, etc.)

**Example document:**
```json
{
  "_id": ObjectId("65d1234567890abcdef12345"),
  "username": "testuser",
  "email": "test@example.com",
  "password": "pbkdf2_sha256$...",
  "first_name": "",
  "last_name": "",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": ISODate("2026-02-17T10:30:00.000Z"),
  "role": "user",
  "plan": "none",
  "credits": 25,
  "streak": 0
}
```

---

## How MongoDB Handles Schema

### Key Differences from Django ORM (SQLite):

1. **No Migrations Required**
   - MongoDB is schema-less
   - Collections are created automatically on first write
   - `python manage.py makemigrations` not needed for MongoEngine models
   - `python manage.py migrate` only runs for Django's contrib apps (admin, sessions)

2. **Dynamic Schema**
   - You can add/remove fields without migrations
   - Existing documents keep old structure until updated
   - New documents have new structure

3. **Indexes**
   - Created explicitly with `model.ensure_indexes()`
   - Run `python manage.py setup_mongodb` to create/update indexes
   - Check indexes in MongoDB Atlas: Collections → Indexes tab

4. **Foreign Keys → References**
   - `ForeignKey` becomes `ReferenceField`
   - Stores MongoDB ObjectId instead of integer
   - No automatic referential integrity (handle in application code)

---

## Switching Between SQLite and MongoDB

Your project supports both databases. Switch by changing `.env`:

### Use MongoDB:
```env
DATABASE_MODE=mongodb
```

### Use SQLite (for testing):
```env
DATABASE_MODE=sqlite
```

**When switching:**
- Restart Django server
- Data is NOT shared between databases
- SQLite uses Django ORM models
- MongoDB uses MongoEngine models

---

## Command Reference

| Command | Purpose |
|---------|---------|
| `python manage.py setup_mongodb` | Setup MongoDB collections & indexes |
| `python manage.py create_mongo_superuser` | Create admin user in MongoDB |
| `python manage.py test_mongo_auth` | Test authentication system |
| `python manage.py runserver` | Start development server |
| `pip install -r requirements.txt` | Install dependencies |

---

## Troubleshooting Guide

### Error: "MongoDB connection failed"

**Check:**
1. `.env` file has correct credentials
2. `MONGO_DB_HOST` is set (not placeholder)
3. Network access configured in Atlas (0.0.0.0/0 for dev)
4. Cluster is not paused (free tier auto-pauses)

**Fix:**
```powershell
# Test connection manually
python
>>> import mongoengine
>>> mongoengine.connect(
...     db='allflex_db',
...     host='mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@YOUR-CLUSTER.mongodb.net/allflex_db?retryWrites=true&w=majority'
... )
```

### Error: "Authentication failed"

**URL encode special characters in password:**
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`

Your password `1Wj1avC1davQ4Vl7` has no special characters, so no encoding needed.

### Error: "No module named 'mongoengine'"

**Fix:**
```powershell
pip install mongoengine pymongo dnspython
```

### Error: "Server selection timeout"

**Possible causes:**
1. Cluster is paused (free tier)
2. IP not whitelisted
3. Incorrect connection string
4. Firewall blocking MongoDB Atlas

**Fix:**
1. Check cluster status in Atlas
2. Add 0.0.0.0/0 to network access (dev only)
3. Verify connection string
4. Disable firewall temporarily to test

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Use strong password (current: `1Wj1avC1davQ4Vl7` is good)
- [ ] Restrict network access to server IP only (remove 0.0.0.0/0)
- [ ] Use M10+ cluster (M0 free tier not for production)
- [ ] Enable MongoDB Atlas backups
- [ ] Set up monitoring & alerts
- [ ] Use environment variables (never hardcode credentials)
- [ ] Enable SSL/TLS
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use connection pooling (already configured in settings.py)

---

## Next Steps

After successful migration:

1. **Seed Credit Packs** (optional):
   ```powershell
   # Create management command for MongoDB
   python manage.py seed_mongo_credit_packs
   ```

2. **Test Full User Flow**:
   - Signup → Login → Dashboard → Find Gyms → Use Visit

3. **Migrate Existing Data** (if you have SQLite data):
   - Export from SQLite
   - Import to MongoDB
   - See: DATA_MIGRATION.md (create if needed)

4. **Update Views** (if needed):
   - Most views use the abstraction layer (`db_utils.py`)
   - No changes needed if using `get_user_model()`, etc.

5. **Test All Features**:
   - [ ] User signup & login
   - [ ] Gym finder (Gemini API)
   - [ ] Use visit (credit deduction)
   - [ ] Plans & credits page
   - [ ] Gym owner dashboard
   - [ ] Admin panel

---

## Support

If you encounter issues:

1. Check MongoDB Atlas dashboard
2. Review connection logs
3. Run `python manage.py test_mongo_auth`
4. Check Django server logs
5. Verify `.env` file

**MongoDB Atlas Monitoring:**
- Metrics → Performance
- Metrics → Network Traffic
- Alerts → Configure email alerts

---

**Migration Status**: 🟢 Ready to Go

All code changes are complete. Follow this guide to complete the migration!
