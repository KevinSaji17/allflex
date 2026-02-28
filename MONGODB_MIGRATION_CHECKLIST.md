# ✅ MongoDB Migration Checklist

## 📋 Complete This Checklist Step-by-Step

---

## Phase 1: MongoDB Atlas Setup ☁️

### [ ] Step 1.1: Create MongoDB Atlas Account
- [ ] Go to https://cloud.mongodb.com/
- [ ] Sign up or login
- [ ] Verify email

### [ ] Step 1.2: Create Cluster
- [ ] Click "Build a Database"
- [ ] Select "M0 (Free)" tier
- [ ] Choose cloud provider (AWS/Google Cloud/Azure)
- [ ] Choose region closest to you (e.g., Mumbai for India)
- [ ] Cluster name: `allflex-cluster`
- [ ] Click "Create Deployment"
- [ ] Wait for cluster to deploy (2-5 minutes)

### [ ] Step 1.3: Create Database User
- [ ] Go to "Database Access" (left sidebar)
- [ ] Click "Add New Database User"
- [ ] Username: `allflex_user` ✅ (already set)
- [ ] Password: `1Wj1avC1davQ4Vl7` ✅ (already set)
- [ ] Privileges: "Read and write to any database"
- [ ] Click "Add User"

### [ ] Step 1.4: Configure Network Access
- [ ] Go to "Network Access" (left sidebar)
- [ ] Click "Add IP Address"
- [ ] Click "Allow Access from Anywhere" (0.0.0.0/0)
- [ ] Click "Confirm"
- [ ] Wait for status to show "Active"

### [ ] Step 1.5: Get Connection String
- [ ] Go to "Database" (left sidebar)
- [ ] Click "Connect" on your cluster
- [ ] Select "Drivers"
- [ ] Copy the connection string
- [ ] Should look like:
  ```
  mongodb+srv://allflex_user:<password>@allflex-cluster.xxxxx.mongodb.net/
  ```
- [ ] Extract the cluster host: `allflex-cluster.xxxxx.mongodb.net`
- [ ] **SAVE THIS!** You need it for the next step

---

## Phase 2: Update Project Configuration 🔧

### [ ] Step 2.1: Update .env File
```powershell
# Open the .env file in your project
notepad .env
```

Find this line:
```env
MONGO_DB_HOST=REPLACE_WITH_YOUR_CLUSTER_URL
```

Replace with your actual cluster URL (from Step 1.5):
```env
MONGO_DB_HOST=allflex-cluster.xxxxx.mongodb.net  # ← YOUR ACTUAL URL
```

**Example:**
```env
MONGO_DB_HOST=allflex-cluster.abc123.mongodb.net
```

Ensure these are set:
```env
DATABASE_MODE=mongodb
MONGO_DB_NAME=allflex_db
MONGO_DB_USER=allflex_user
MONGO_DB_PASSWORD=1Wj1avC1davQ4Vl7
MONGO_DB_HOST=allflex-cluster.xxxxx.mongodb.net  # ← UPDATE THIS
```

Save and close the file.

### [ ] Step 2.2: Verify Packages Installed
Packages are already installed! ✅
- mongoengine
- pymongo
- dnspython

---

## Phase 3: Test Connection & Setup MongoDB 🔌

### [ ] Step 3.1: Check Readiness
```powershell
cd "c:\Users\Benedict Moncy\Documents\Projects\Saji Project\allflex"
.\venv\Scripts\Activate.ps1
python manage.py check_mongo_ready
```

**Expected output:**
```
✅ ALL CHECKS PASSED!
```

If you see errors:
- Check MONGO_DB_HOST is set correctly in .env
- Verify network access in MongoDB Atlas
- Ensure cluster is active (not paused)

### [ ] Step 3.2: Setup MongoDB Collections
```powershell
python manage.py setup_mongodb
```

**Expected output:**
```
✅ Connected to MongoDB: allflex_db
✅ Indexes created for users
✅ Indexes created for gyms
... (more collections)
✅ MongoDB Setup Complete!
```

### [ ] Step 3.3: Create Superuser
```powershell
python manage.py create_mongo_superuser
```

**Interactive prompts:**
- Username: `admin` (or your choice)
- Email: `admin@allflex.com`
- Password: `AdminPass123` (or your choice)

**Expected output:**
```
✅ Superuser "admin" created successfully!
```

### [ ] Step 3.4: Test Authentication
```powershell
python manage.py test_mongo_auth
```

**Interactive test:**
- Enter your admin username
- Enter password
- Should show: ✅ Authentication Successful!

### [ ] Step 3.5: Seed Credit Packs (Optional)
```powershell
python manage.py seed_mongo_credit_packs
```

**Expected output:**
```
✅ Created 7 credit pack(s)
```

---

## Phase 4: Test the Application 🧪

### [ ] Step 4.1: Start Development Server
```powershell
python manage.py runserver
```

**Expected output:**
```
✅ Connected to MongoDB: allflex_db
Starting development server at http://127.0.0.1:8000/
```

### [ ] Step 4.2: Test Signup
1. [ ] Open browser: http://127.0.0.1:8000/accounts/signup/
2. [ ] Fill signup form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPass123`
3. [ ] Click "Sign Up"
4. [ ] Should redirect to login page ✅

### [ ] Step 4.3: Test Login
1. [ ] Go to: http://127.0.0.1:8000/accounts/login/
2. [ ] Login with `testuser` / `TestPass123`
3. [ ] Should redirect to dashboard ✅

### [ ] Step 4.4: Verify 25 Demo Credits
1. [ ] On dashboard, check top of page
2. [ ] Should show: "Available Credits: 25" ✅

### [ ] Step 4.5: Test Gym Finder
1. [ ] On dashboard, enter pincode (e.g., `400001`)
2. [ ] Click "Find Gyms"
3. [ ] Should show demo gyms ✅

### [ ] Step 4.6: Test "Use Visit" (Optional)
1. [ ] Click "Use 1 Visit (5 credits)" on a Tier 1 gym
2. [ ] Should show success message
3. [ ] Credits should decrease: 25 → 20 ✅

---

## Phase 5: Verify Data in MongoDB Atlas 🔍

### [ ] Step 5.1: View Users Collection
1. [ ] Go to MongoDB Atlas: https://cloud.mongodb.com
2. [ ] Navigate to: Database → Browse Collections
3. [ ] Database: `allflex_db`
4. [ ] Collection: `users`
5. [ ] Should see your users:
   - admin (superuser)
   - testuser
6. [ ] Click on a document to see fields:
   - username ✅
   - email ✅
   - password (hashed) ✅
   - credits: 25 ✅
   - role: "user" ✅
   - is_active: true ✅

### [ ] Step 5.2: View Other Collections
Check these collections exist:
- [ ] `users`
- [ ] `gyms`
- [ ] `bookings`
- [ ] `credit_packs`
- [ ] `credit_transactions`
- [ ] `gym_bookings`
- [ ] `ratings`
- [ ] `payout_requests`

### [ ] Step 5.3: View Indexes
1. [ ] In MongoDB Atlas, select `users` collection
2. [ ] Click "Indexes" tab
3. [ ] Should see indexes:
   - _id_ (default)
   - username
   - email
   - Other compound indexes

---

## Phase 6: Final Verification ✅

### [ ] Functionality Checklist
- [ ] Signup creates user in MongoDB ✅
- [ ] Login authenticates against MongoDB ✅
- [ ] Dashboard loads with user data ✅
- [ ] Credits display correctly ✅
- [ ] User data visible in Atlas dashboard ✅

### [ ] Performance Checklist
- [ ] Page load time < 2 seconds ✅
- [ ] No connection errors in console ✅
- [ ] Indexes created (check Atlas) ✅

### [ ] Security Checklist
- [ ] Password is hashed (not plain text) ✅
- [ ] .env file not committed to Git ✅
- [ ] Network access configured ✅

---

## 🎉 Migration Complete!

When all checkboxes are marked:

✅ **Your AllFlex project is now running on MongoDB Atlas!**

---

## 📚 Reference Documents

| Document | Purpose |
|----------|---------|
| [MONGODB_SETUP.md](MONGODB_SETUP.md) | Detailed Atlas setup guide |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Complete migration workflow |
| [MONGODB_QUICK_REFERENCE.md](MONGODB_QUICK_REFERENCE.md) | Quick commands & troubleshooting |
| [MONGODB_BEST_PRACTICES.md](MONGODB_BEST_PRACTICES.md) | Production guidelines |
| [MONGODB_IMPLEMENTATION_SUMMARY.md](MONGODB_IMPLEMENTATION_SUMMARY.md) | All changes made |

---

## 🆘 Troubleshooting

### Issue: "MongoDB connection failed"
**Solution:**
1. Check MONGO_DB_HOST in .env is correct
2. Verify cluster is active in Atlas (not paused)
3. Check network access (0.0.0.0/0 added)

### Issue: "Authentication failed"
**Solution:**
1. Verify username/password in Atlas matches .env
2. Check password doesn't need URL encoding
3. Try creating a new database user in Atlas

### Issue: "Server selection timeout"
**Solution:**
1. Check internet connection
2. Verify firewall not blocking MongoDB
3. Check cluster status in Atlas dashboard

### Issue: User not showing in Atlas
**Solution:**
1. Refresh Atlas dashboard (Browser Collections)
2. Wait 10-30 seconds for replication
3. Check database name is `allflex_db`

---

## 🎯 Next Steps After Migration

1. **Migrate Existing Data** (if you have SQLite data):
   - Export from SQLite
   - Import to MongoDB
   - Create migration script

2. **Enable Production Features**:
   - Upgrade to M10+ cluster
   - Restrict network access to server IP
   - Enable automated backups
   - Set up monitoring alerts

3. **Optimize Performance**:
   - Add more indexes for common queries
   - Enable caching (Redis)
   - Optimize image storage (S3/Cloudinary)

4. **Test All Features**:
   - Gym owner dashboard
   - Admin panel
   - Payment flow (when implemented)
   - QR code system (when implemented)

---

**Print this checklist and mark items as you complete them!** ✨
