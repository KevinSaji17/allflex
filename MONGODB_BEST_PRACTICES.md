# MongoDB Best Practices for AllFlex

## 🔐 Security Best Practices

### 1. Password Security

**✅ Current Status:**
- Password: `1Wj1avC1davQ4Vl7` (Strong - 16 chars, alphanumeric)
- Stored in: `.env` file (not committed to Git)

**Best Practices:**
```env
# ✅ GOOD: Use environment variables
MONGO_DB_PASSWORD=1Wj1avC1davQ4Vl7

# ❌ BAD: Hardcoded in settings.py
password = "1Wj1avC1davQ4Vl7"  # Never do this!
```

**Password Requirements:**
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers
- Avoid common words
- Rotate passwords periodically (every 90 days)

### 2. Network Access Control

**Development:**
```
IP Whitelist: 0.0.0.0/0 (Allow from anywhere)
```
- ⚠️ Convenient for testing
- ⚠️ Less secure
- ✅ Acceptable for development only

**Production:**
```
IP Whitelist: 
- Your server IP: 203.0.113.42
- Office IP: 198.51.100.0/24
- Backup server: 192.0.2.100
```
- ✅ Restrict to known IPs only
- ✅ Update when server changes
- ✅ Use VPC peering for cloud deployments

### 3. Connection String Security

**✅ Secure (using environment variables):**
```python
# In settings.py
MONGODB_CONNECTION_STRING = (
    f"mongodb+srv://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}/"
    f"{MONGO_DB_NAME}?retryWrites=true&w=majority&appName=AllFlex"
)
```

**❌ Insecure (hardcoded):**
```python
# DON'T DO THIS!
MONGODB_CONNECTION_STRING = "mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@..."
```

### 4. Database User Privileges

**Current Setup:**
- User: `allflex_user`
- Privilege: Read and write to any database

**Production Recommendations:**
```
1. Create separate users for different environments:
   - allflex_prod_user (production)
   - allflex_dev_user (development)
   - allflex_readonly (analytics)

2. Limit privileges:
   - Production: Read/write to specific database only
   - Development: Read/write to dev database
   - Analytics: Read-only access
```

---

## ⚡ Performance Best Practices

### 1. Indexing Strategy

**Already Implemented:**
```python
# In mongo_models.py
meta = {
    'collection': 'users',
    'indexes': [
        'username',  # Single field index
        'email',     # Single field index
        {'fields': ['is_active', 'role']},  # Compound index
    ]
}
```

**Key Indexing Rules:**
- ✅ Index fields used in `filter()` queries
- ✅ Index fields used for sorting
- ✅ Create compound indexes for common query patterns
- ❌ Don't over-index (slows down writes)

**Monitor Index Usage:**
```python
# In MongoDB Atlas
# Performance → Indexes → View Index Stats
# Check: Hit Rate, Scan Rate
```

### 2. Connection Pooling

**Already Configured:**
```python
# In settings.py
mongoengine.connect(
    db=MONGO_DB_NAME,
    host=MONGODB_CONNECTION_STRING,
    maxPoolSize=50,      # Max connections in pool
    minPoolSize=10,      # Min connections to maintain
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
)
```

**Pool Size Guidelines:**
- Development: 10-20 connections
- Production (low traffic): 50-100 connections
- Production (high traffic): 100-500 connections

**Formula:**
```
maxPoolSize = (concurrent_users × 2) + 10
```

### 3. Query Optimization

**✅ Good Queries:**
```python
# Use indexed fields
user = UserProfile.objects.get(username='testuser')

# Limit results
recent_bookings = GymBooking.objects.filter(user=user)[:10]

# Project only needed fields
users = UserProfile.objects.only('username', 'email')
```

**❌ Bad Queries:**
```python
# Avoid loading all documents
all_users = UserProfile.objects.all()  # Could be millions!

# Don't filter on non-indexed fields repeatedly
gyms = Gym.objects.filter(description__contains='pool')  # Slow!
```

**Query Performance Tips:**
1. Use `only()` to select specific fields
2. Use `exclude()` to omit large fields
3. Paginate results (10-50 per page)
4. Cache frequently accessed data

### 4. Batch Operations

**✅ Efficient:**
```python
# Bulk insert
gyms = [
    Gym(name=f'Gym {i}', owner=owner, tier=1, ...)
    for i in range(100)
]
Gym.objects.insert(gyms)  # Single database call
```

**❌ Inefficient:**
```python
# Individual inserts
for i in range(100):
    gym = Gym(name=f'Gym {i}', ...)
    gym.save()  # 100 database calls!
```

---

## 🏗️ Architecture Best Practices

### 1. Database Abstraction Layer

**Already Implemented: `accounts/db_utils.py`**

```python
# Usage in views
from accounts.db_utils import get_user_model, is_mongodb

User = get_user_model()  # Works with both MongoDB & SQLite

# Create user
user = create_user(username='test', email='test@example.com', password='pass')

# Check database mode
if is_mongodb():
    # MongoDB-specific logic
else:
    # Django ORM logic
```

**Benefits:**
- ✅ Easy to switch between databases
- ✅ Centralized database logic
- ✅ Easier testing (mock database)
- ✅ Future-proof (add PostgreSQL support later)

### 2. Model Best Practices

**Use Proper Field Types:**
```python
# ✅ Good
credits = IntField(default=0, min_value=0)
price = FloatField(min_value=0.0)
status = StringField(choices=STATUS_CHOICES)
created_at = DateTimeField(default=datetime.utcnow)

# ❌ Avoid
credits = StringField()  # Should be IntField
price = StringField()    # Should be FloatField
```

**Use Validators:**
```python
from mongoengine import ValidationError

class UserProfile(Document):
    email = EmailField(required=True, unique=True)
    
    def clean(self):
        # Custom validation
        if not self.email.endswith('@example.com'):
            raise ValidationError('Email must be from example.com')
```

### 3. Error Handling

**Always Handle MongoDB Exceptions:**
```python
from mongoengine.errors import DoesNotExist, NotUniqueError

try:
    user = UserProfile.objects.get(username='test')
except DoesNotExist:
    # Handle user not found
    return JsonResponse({'error': 'User not found'}, status=404)
except NotUniqueError:
    # Handle duplicate username
    return JsonResponse({'error': 'Username already exists'}, status=400)
```

---

## 📊 Monitoring & Logging

### 1. MongoDB Atlas Monitoring

**Enable Alerts:**
1. Go to: Alerts → Create Alert
2. Set up alerts for:
   - High CPU usage (>80%)
   - High connection count (>90% of max)
   - Slow queries (>100ms)
   - Authentication failures

**Monitor Metrics:**
- **Performance**: Query execution time, index usage
- **Connections**: Active connections, connection pool stats
- **Storage**: Database size, collection size
- **Network**: Data transfer in/out

### 2. Application Logging

**Add Logging to Your App:**
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'mongodb.log',
        },
    },
    'loggers': {
        'mongoengine': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

**Log Important Events:**
```python
import logging
logger = logging.getLogger('mongoengine')

# Log user creation
logger.info(f'User created: {user.username} ({user.email})')

# Log authentication
logger.info(f'User logged in: {user.username}')

# Log errors
logger.error(f'MongoDB connection failed: {e}')
```

---

## 🔄 Backup & Recovery

### 1. MongoDB Atlas Backups (Recommended)

**M10+ Clusters (Paid Tier):**
- Automated continuous backups
- Point-in-time recovery
- Snapshot retention: 7-90 days
- Restore to new cluster

**M0 Free Tier:**
- No automated backups
- Manual export required

### 2. Manual Backup

**Export All Collections:**
```powershell
# Install MongoDB Database Tools
# Download from: https://www.mongodb.com/try/download/database-tools

# Export entire database
mongodump --uri="mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@allflex-cluster.xxxxx.mongodb.net/allflex_db" --out=./backup

# Restore database
mongorestore --uri="mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@allflex-cluster.xxxxx.mongodb.net/allflex_db" ./backup/allflex_db
```

**Export as JSON:**
```powershell
# Export users collection
mongoexport --uri="mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@allflex-cluster.xxxxx.mongodb.net/allflex_db" --collection=users --out=users.json

# Import users collection
mongoimport --uri="mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@allflex-cluster.xxxxx.mongodb.net/allflex_db" --collection=users --file=users.json
```

**Automated Backup Script:**
```python
# backup_mongodb.py
import subprocess
from datetime import datetime

backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
connection_string = "mongodb+srv://allflex_user:1Wj1avC1davQ4Vl7@..."

subprocess.run([
    'mongodump',
    f'--uri={connection_string}',
    f'--out={backup_dir}'
])
print(f'Backup created: {backup_dir}')
```

**Backup Schedule:**
- Daily: Full database backup
- Weekly: Archive to long-term storage
- Monthly: Test restore procedure

---

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] **Environment Variables Set**
  - [ ] `DATABASE_MODE=mongodb`
  - [ ] `MONGO_DB_PASSWORD` (strong, rotated)
  - [ ] `SECRET_KEY` (unique, not default)
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS` (domain name, server IP)

- [ ] **MongoDB Atlas Configuration**
  - [ ] M10+ cluster (not M0 free tier)
  - [ ] Network access: Server IP only (not 0.0.0.0/0)
  - [ ] Database user: Production credentials
  - [ ] Backups enabled
  - [ ] Alerts configured

- [ ] **Security**
  - [ ] SSL/TLS enabled
  - [ ] Firewall configured
  - [ ] Rate limiting enabled
  - [ ] CSRF protection enabled
  - [ ] XSS protection enabled

- [ ] **Performance**
  - [ ] Indexes created (`python manage.py setup_mongodb`)
  - [ ] Connection pooling configured
  - [ ] Caching enabled (Redis/Memcached)
  - [ ] Static files served via CDN

### Post-Deployment

- [ ] **Monitoring**
  - [ ] MongoDB Atlas alerts active
  - [ ] Application logging enabled
  - [ ] Error tracking (Sentry, Rollbar)
  - [ ] Performance monitoring (New Relic, Datadog)

- [ ] **Testing**
  - [ ] Test all critical flows
  - [ ] Load testing completed
  - [ ] Backup/restore tested
  - [ ] Failover tested

---

## 📈 Scaling Recommendations

### Vertical Scaling (Single Server)

**When to scale:**
- CPU usage consistently >70%
- Memory usage >80%
- Query latency >100ms

**MongoDB Atlas Tiers:**
```
M10:  2GB RAM,  10GB storage  → $0.08/hr  (Small apps)
M20:  4GB RAM,  20GB storage  → $0.20/hr  (Medium apps)
M30:  8GB RAM,  40GB storage  → $0.54/hr  (Large apps)
M40: 16GB RAM,  80GB storage  → $1.04/hr  (High traffic)
```

### Horizontal Scaling (Sharding)

**When to scale:**
- Database size >100GB
- Write throughput >10,000 ops/sec
- Single server can't handle traffic

**Sharding Strategy:**
```python
# Shard by user
{
    'shard_key': 'user_id',
    'strategy': 'hashed'
}

# Shard by location
{
    'shard_key': 'location',
    'strategy': 'range'
}
```

---

## 🛠️ Development Workflow

### Local Development

```powershell
# 1. Use MongoDB (cloud)
DATABASE_MODE=mongodb python manage.py runserver

# 2. Use SQLite (local, faster for testing)
DATABASE_MODE=sqlite python manage.py runserver

# 3. Switch databases anytime by changing .env
```

### Testing

```python
# tests.py
from django.test import TestCase
from accounts.db_utils import is_mongodb, get_user_model

class UserTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        
        if is_mongodb():
            # MongoDB test setup
            self.user = User(username='test', email='test@example.com')
            self.user.set_password('password')
            self.user.save()
        else:
            # Django ORM test setup
            self.user = User.objects.create_user(
                username='test',
                email='test@example.com',
                password='password'
            )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'test')
```

---

## 📝 Code Style Guidelines

### 1. Model Naming

```python
# ✅ Good
class UserProfile(Document):
    username = StringField()
    
# ❌ Bad
class user_profile(Document):  # Use PascalCase
    user_name = StringField()  # Field names can be snake_case
```

### 2. Query Naming

```python
# ✅ Descriptive
active_users = UserProfile.objects.filter(is_active=True)
recent_bookings = GymBooking.objects.filter(user=user).order_by('-booked_at')[:10]

# ❌ Unclear
data = UserProfile.objects.filter(is_active=True)
x = GymBooking.objects.filter(user=user)[:10]
```

### 3. Error Messages

```python
# ✅ User-friendly
return JsonResponse({
    'error': 'Insufficient credits. You need 5 credits to book this gym.',
    'required': 5,
    'available': user.credits
}, status=400)

# ❌ Not helpful
return JsonResponse({'error': 'Error'}, status=400)
```

---

## 🎯 Summary

**Key Takeaways:**

1. **Security**: Use environment variables, restrict network access, rotate passwords
2. **Performance**: Create indexes, use connection pooling, optimize queries
3. **Monitoring**: Enable Atlas alerts, log important events, track metrics
4. **Backups**: Enable automated backups, test restore procedures
5. **Scaling**: Start with M10, monitor metrics, scale when needed

**Your Current Setup:**
- ✅ MongoDB Atlas (cloud)
- ✅ MongoEngine ODM
- ✅ Custom authentication backend
- ✅ Database abstraction layer
- ✅ Proper indexing
- ✅ Connection pooling
- ✅ Environment variables

**Production-Ready Checklist:**
- ⚠️ Change to M10+ cluster (currently using free tier for dev)
- ⚠️ Restrict network access (currently 0.0.0.0/0)
- ⚠️ Enable automated backups
- ⚠️ Set up monitoring alerts
- ✅ Everything else is configured!

---

**Questions? Check:**
- [MONGODB_SETUP.md](./MONGODB_SETUP.md) - Initial setup guide
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Step-by-step migration
- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [MongoEngine Docs](http://docs.mongoengine.org/)
