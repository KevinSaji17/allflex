# MongoDB Migration - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Update .env file
```env
DATABASE_MODE=mongodb
MONGO_DB_HOST=your-cluster.xxxxx.mongodb.net  # ← GET THIS FROM ATLAS
```

### 2. Install packages
```powershell
pip install -r requirements.txt
```

### 3. Setup MongoDB
```powershell
python manage.py setup_mongodb
python manage.py create_mongo_superuser
python manage.py runserver
```

---

## 📋 Command Cheat Sheet

| Task | Command |
|------|---------|
| Setup MongoDB | `python manage.py setup_mongodb` |
| Create admin user | `python manage.py create_mongo_superuser` |
| Test authentication | `python manage.py test_mongo_auth` |
| Seed credit packs | `python manage.py seed_mongo_credit_packs` |
| Run server | `python manage.py runserver` |
| Switch to SQLite | Set `DATABASE_MODE=sqlite` in `.env` |
| Switch to MongoDB | Set `DATABASE_MODE=mongodb` in `.env` |

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| MongoDB Atlas | https://cloud.mongodb.com |
| Local App | http://127.0.0.1:8000 |
| Signup | http://127.0.0.1:8000/accounts/signup/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Dashboard | http://127.0.0.1:8000/dashboard/ |

---

## 📦 Collections Created

- `users` - User accounts (UserProfile)
- `gyms` - Gym listings
- `bookings` - Gym bookings
- `ratings` - Gym reviews
- `credit_packs` - Credit pack offerings
- `user_credit_packs` - User-owned credit packs
- `credit_transactions` - Credit purchase/usage log
- `gym_bookings` - Booking records with status
- `payout_requests` - Gym owner payout requests
- `user_credit_balances` - User credit balances

---

## 🔑 Environment Variables

```env
# Required
DATABASE_MODE=mongodb
MONGO_DB_NAME=allflex_db
MONGO_DB_USER=allflex_user
MONGO_DB_PASSWORD=1Wj1avC1davQ4Vl7
MONGO_DB_HOST=your-cluster.xxxxx.mongodb.net  # GET FROM ATLAS

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional
GEMINI_API_KEY=your-gemini-key
```

---

## 🔍 Verify Connection

### Test in Python:
```python
python
>>> import mongoengine
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> mongoengine.connect(
...     db='allflex_db',
...     host=f'mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@YOUR-CLUSTER.mongodb.net/allflex_db'
... )
>>> print("✅ Connected!")
```

### Test via Management Command:
```powershell
python manage.py setup_mongodb
```

---

## ⚠️ Troubleshooting

| Error | Solution |
|-------|----------|
| "MongoDB connection failed" | Check `MONGO_DB_HOST` in `.env` |
| "Authentication failed" | Verify password in `.env` |
| "Server selection timeout" | Check network access in Atlas (add 0.0.0.0/0) |
| "No module named mongoengine" | Run `pip install -r requirements.txt` |
| "Cluster paused" | Wake up cluster in Atlas (free tier auto-pauses) |

---

## 📝 Next Steps After Setup

1. **Create superuser**: `python manage.py create_mongo_superuser`
2. **Seed credit packs**: `python manage.py seed_mongo_credit_packs`
3. **Start server**: `python manage.py runserver`
4. **Test signup**: http://127.0.0.1:8000/accounts/signup/
5. **Check Atlas**: Database → Browse Collections → users

---

## 🎯 Test Checklist

- [ ] Connection successful (`setup_mongodb`)
- [ ] Superuser created
- [ ] Can login with superuser
- [ ] Signup creates user in MongoDB
- [ ] User appears in Atlas dashboard
- [ ] Credits awarded on signup (25)
- [ ] Credit packs seeded
- [ ] Dashboard loads correctly
- [ ] Gym finder works (enter pincode)
- [ ] "Use visit" deducts credits

---

## 📚 Full Documentation

- **Setup Guide**: [MONGODB_SETUP.md](./MONGODB_SETUP.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **Best Practices**: [MONGODB_BEST_PRACTICES.md](./MONGODB_BEST_PRACTICES.md)
- **Project Overview**: [README.md](./README.md)

---

## 🆘 Get Help

1. Check error message
2. Review [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) troubleshooting section
3. Verify `.env` file settings
4. Check MongoDB Atlas dashboard
5. Review Django server logs
