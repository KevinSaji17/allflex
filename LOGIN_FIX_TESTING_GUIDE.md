# 🧪 Login Fix Verification Guide

## ✅ How to Test if Login is Fixed

Follow these steps **in order** to verify that all authentication issues are resolved.

---

## 🔧 **Step 1: Verify Environment Setup**

### Check your `.env` file
```bash
cat .env
```

**Expected output:**
```dotenv
DATABASE_MODE=mongodb
MONGO_DB_NAME=allflex_db
MONGO_DB_USER=allflex_user
MONGO_DB_PASSWORD=1Wj1avC1davQ4Vl7
MONGO_DB_HOST=allflex-cluster.3aw66c7.mongodb.net
DEBUG=True
```

✅ **Pass:** All MongoDB credentials are set correctly  
❌ **Fail:** Update `.env` file with correct MongoDB Atlas credentials

---

## 🗄️ **Step 2: Verify MongoDB Connection**

### Start the development server
```powershell
python manage.py runserver
```

**Expected output:**
```
✅ Connected to MongoDB: allflex_db
System check identified no issues (0 silenced).
Django version 5.2, using settings 'allflex.settings'
Starting development server at http://127.0.0.1:8000/
```

✅ **Pass:** See "Connected to MongoDB" message  
❌ **Fail:** Check MongoDB Atlas network access (IP whitelist), credentials, or cluster status

---

## 👤 **Step 3: Create a Test User**

### Option A: Create Superuser (Admin)
```powershell
python manage.py create_mongo_superuser
```

**Follow prompts:**
```
Username: admin
Email: admin@test.com
Password: admin123
Password (again): admin123
```

**Expected output:**
```
✅ Superuser "admin" created successfully!
```

### Option B: Test User Creation Script
```powershell
python manage.py test_mongo_auth
```

**Expected output:**
```
🎉 MongoDB authentication is working correctly!
```

✅ **Pass:** User created successfully  
❌ **Fail:** Check error message and verify MongoDB connection

---

## 🔐 **Step 4: Test Login via Web Interface**

### 4.1 Navigate to Login Page
1. Open browser: `http://127.0.0.1:8000/accounts/login/`
2. Check that login form appears

✅ **Pass:** Login form loads correctly  
❌ **Fail:** Check server logs for template errors

### 4.2 Attempt Login
**Enter credentials:**
- **Username:** `admin` (or username you created)
- **Password:** `admin123` (or password you set)

**Click:** "Sign in" button

### 4.3 Check Login Success
**Expected behavior:**
- Redirected to appropriate dashboard based on role:
  - **Admin** → `/adminpanel/dashboard/`
  - **Gym Owner** → `/gyms/dashboard/`
  - **User** → `/users/dashboard/`

✅ **Pass:** Logged in successfully and redirected to correct dashboard  
❌ **Fail:** See troubleshooting section below

---

## 📝 **Step 5: Test Signup via Web Interface**

### 5.1 Navigate to Signup Page
1. Open browser: `http://127.0.0.1:8000/accounts/signup/`
2. Check that signup form appears

### 5.2 Create New User
**Fill in form:**
- **Username:** `testuser`
- **Email:** `test@example.com`
- **Role:** `User` (select from dropdown)
- **Password:** `testpass123`
- **Password confirmation:** `testpass123`

**Click:** "Create account" button

### 5.3 Check Signup Success
**Expected behavior:**
- Redirected to login page: `/accounts/login/`
- Success message appears

✅ **Pass:** User created, redirected to login  
❌ **Fail:** See troubleshooting section below

### 5.4 Login with New User
- **Username:** `testuser`
- **Password:** `testpass123`
- Should redirect to user dashboard with **25 demo credits**

✅ **Pass:** New user can login successfully  
❌ **Fail:** Check MongoDB for user creation

---

## 🔍 **Step 6: Verify Data in MongoDB Atlas**

### 6.1 Access MongoDB Atlas
1. Go to: [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Navigate to: **Database** → **Browse Collections**
3. Database: `allflex_db`
4. Collection: `users`

### 6.2 Check User Document
**Click on your user document to verify fields:**

```json
{
  "_id": ObjectId("..."),
  "username": "testuser",                    // ✅ Should exist
  "email": "test@example.com",               // ✅ Should exist
  "password": "pbkdf2_sha256$...",          // ✅ Should be hashed
  "first_name": "",                          // ✅ Should exist (can be empty)
  "last_name": "",                           // ✅ Should exist (can be empty)
  "is_active": true,                         // ✅ Should be true
  "is_staff": false,                         // ✅ Should be false (true for admin)
  "is_superuser": false,                     // ✅ Should be false (true for admin)
  "role": "user",                            // ✅ Should match selection
  "plan": "none",                            // ✅ Should exist
  "credits": 25,                             // ✅ Should be 25 for new users
  "streak": 0,                               // ✅ Should exist
  "qr_code": "",                             // ✅ Should exist (can be empty)
  "date_joined": ISODate("2026-02-19..."),  // ✅ Should exist
  "last_login": ISODate("2026-02-19...")    // ✅ Should update on login
}
```

✅ **Pass:** All fields exist and have correct values  
❌ **Fail:** If fields are missing, the mongo_models.py fix didn't apply

---

## 🧪 **Step 7: Test Session Persistence**

### 7.1 Login and Navigate
1. Login at `/accounts/login/`
2. Navigate to different pages (dashboard, gyms, etc.)
3. User should **remain logged in**

### 7.2 Close and Reopen Browser
1. Close browser completely
2. Reopen and go to `http://127.0.0.1:8000/users/dashboard/`
3. Should **still be logged in** (session persists for 7 days)

✅ **Pass:** Session persists across page navigation and browser restarts  
❌ **Fail:** Check session serializer and MongoDB connection

---

## 🚪 **Step 8: Test Logout**

### 8.1 Logout
1. Click logout link (usually in navbar)
2. Or navigate to: `/accounts/logout/`

### 8.2 Verify Logout
**Expected behavior:**
- Redirected to home page: `/users/home/`
- User is no longer authenticated
- Attempting to access `/users/dashboard/` redirects to login

✅ **Pass:** Logout works, protected pages redirect to login  
❌ **Fail:** Check logout URL configuration

---

## 🎭 **Step 9: Test Role-Based Redirects**

### 9.1 Test Admin User
```powershell
# Create admin if not exists
python manage.py create_mongo_superuser
# Username: admin, Password: admin123
```

**Login as admin:**
- Should redirect to: `/adminpanel/dashboard/`
- Should see: Admin dashboard with user management, gym approvals, payouts

### 9.2 Test Gym Owner
**Create gym owner via signup:**
- Username: `gymowner`
- Role: **Gym Owner**
- Password: `gym123`

**Login as gym owner:**
- Should redirect to: `/gyms/dashboard/`
- Should see: Gym management features

### 9.3 Test Regular User
**Create user via signup:**
- Username: `regularuser`
- Role: **User**
- Password: `user123`

**Login as user:**
- Should redirect to: `/users/dashboard/`
- Should see: Credit balance (25 credits), gym booking options

✅ **Pass:** Each role redirects to correct dashboard  
❌ **Fail:** Check role_based_redirect view in accounts/views.py

---

## 🐛 **Troubleshooting Common Issues**

### ❌ **Issue 1: "Authentication Failed"**

**Symptoms:** Login form returns error, user cannot login

**Possible Causes:**
1. **MongoDB not connected**
   ```powershell
   # Check server startup logs for "Connected to MongoDB"
   python manage.py runserver
   ```

2. **User doesn't exist in MongoDB**
   ```powershell
   # Create user
   python manage.py create_mongo_superuser
   ```

3. **Wrong password**
   - Passwords are case-sensitive
   - Ensure you're entering the correct password

4. **User is inactive**
   - Check MongoDB: `is_active` field should be `true`

**Fix:**
```powershell
# Test authentication directly
python manage.py test_mongo_auth
```

---

### ❌ **Issue 2: "DoesNotExist: UserProfile matching query does not exist"**

**Symptoms:** Error page appears after login attempt

**Cause:** MongoDB UserProfile model fields were missing (this was the main bug)

**Fix:** Already fixed! The mongo_models.py update added all missing fields.

**Verify fix:**
```python
# In Django shell
python manage.py shell

from accounts.mongo_models import UserProfile
user = UserProfile.objects.first()
print(user.username)  # Should print username
print(user.email)     # Should print email
print(user.credits)   # Should print credit amount
```

---

### ❌ **Issue 3: "Cannot import name 'UserProfile'"**

**Symptoms:** Import error when running server

**Cause:** Circular import or incorrect import path

**Fix:**
```python
# Use db_utils instead
from accounts.db_utils import get_user_model
User = get_user_model()
```

---

### ❌ **Issue 4: Server Won't Start - MongoDB Connection Error**

**Symptoms:**
```
❌ MongoDB connection failed: ...
```

**Possible Causes:**
1. **Wrong credentials** - Check `.env` file
2. **IP not whitelisted** - Add 0.0.0.0/0 in MongoDB Atlas Network Access
3. **Cluster paused** - Free tier clusters pause after inactivity
4. **Wrong connection string** - Verify `MONGO_DB_HOST`

**Fix:**
1. Check MongoDB Atlas → Network Access → Add IP Address → Allow from Anywhere (0.0.0.0/0)
2. Check MongoDB Atlas → Database → Resume cluster if paused
3. Verify `.env` credentials match MongoDB Atlas user

---

### ❌ **Issue 5: Signup Form Doesn't Show Role Field**

**Symptoms:** Role dropdown missing from signup form

**Cause:** Template issue or form not rendering correctly

**Check template:**
```html
<!-- In accounts/templates/registration/signup.html -->
{% for field in form %}
    <!-- Should include role field -->
{% endfor %}
```

**Fix:** Ensure SignUpForm includes `'role'` in fields

---

### ❌ **Issue 6: New Users Get 0 Credits Instead of 25**

**Symptoms:** New users have 0 credits instead of 25 demo credits

**Cause:** Signup view not setting credits

**Fix:** Already fixed in accounts/views.py - SignUpView now sets `credits=25`

**Verify:**
1. Create new user via signup
2. Check MongoDB: `credits` field should be `25`
3. Check dashboard after login: Should show "25 credits"

---

## 📊 **Success Checklist**

Use this checklist to confirm everything works:

- [ ] ✅ Development server starts without errors
- [ ] ✅ "Connected to MongoDB" message appears in logs
- [ ] ✅ Superuser created successfully
- [ ] ✅ Login page loads at `/accounts/login/`
- [ ] ✅ Can login with correct credentials
- [ ] ✅ Redirected to appropriate dashboard based on role
- [ ] ✅ Signup page loads at `/accounts/signup/`
- [ ] ✅ New users can be created via signup form
- [ ] ✅ New users get 25 demo credits
- [ ] ✅ New users can login immediately after signup
- [ ] ✅ Session persists across page navigation
- [ ] ✅ Session persists after browser restart
- [ ] ✅ Logout works correctly
- [ ] ✅ User data visible in MongoDB Atlas with all fields
- [ ] ✅ Admin users redirect to admin dashboard
- [ ] ✅ Gym owners redirect to gym dashboard
- [ ] ✅ Regular users redirect to user dashboard

---

## 🎉 **Expected Final Result**

When everything works correctly:

1. **Server starts cleanly** with MongoDB connection confirmed
2. **Users can signup** and immediately login
3. **Authentication persists** across sessions
4. **Role-based redirects** work correctly
5. **All user data** is properly stored in MongoDB Atlas
6. **Credits system** initializes correctly (25 credits for new users)

---

## 📞 **If Problems Persist**

### Check these files match the fixes:

1. **accounts/mongo_models.py**
   - UserProfile class should have ALL fields defined (username, email, password, etc.)
   - Line ~28: Should see field definitions like `username = StringField(...)`

2. **accounts/forms.py**
   - Should use `get_user_model()` from db_utils
   - Should NOT import `.models` directly

3. **accounts/views.py**
   - SignUpView should set `credits=25` and `role=...`

### View server logs:
```powershell
# Run with verbose output
python manage.py runserver --verbosity 2
```

### Check Django shell:
```powershell
python manage.py shell
```

```python
# Test imports
from accounts.db_utils import is_mongodb, get_user_model
print(f"Database mode: {'MongoDB' if is_mongodb() else 'SQLite'}")

User = get_user_model()
print(f"User model: {User}")

# List all users
for user in User.objects.all():
    print(f"User: {user.username}, Email: {user.email}, Credits: {user.credits}")
```

---

**Testing Guide Created:** February 19, 2026  
**Status:** All fixes implemented ✅  
**Next Step:** Run through this checklist to verify login works!
