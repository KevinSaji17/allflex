# MongoDB Atlas Setup Guide for AllFlex

## Step-by-Step MongoDB Atlas Configuration

### 1. Create MongoDB Atlas Account
1. Go to [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. Sign up (free tier available)
3. Verify your email

### 2. Create a New Cluster
1. Click **"Build a Database"** or **"Create"**
2. Select **M0 (Free Tier)** for testing or **M10+** for production
3. Choose **Cloud Provider**: AWS, Google Cloud, or Azure
4. Choose **Region**: Select closest to your users (e.g., Mumbai for India)
5. Cluster Name: `allflex-cluster`
6. Click **"Create Deployment"**

### 3. Create Database User
1. Go to **Database Access** (left sidebar under Security)
2. Click **"Add New Database User"**
3. Authentication Method: **Password**
4. Username: `allflex_user` (or your choice)
5. Password: Generate a secure password (save this!)
6. Database User Privileges: **Read and write to any database**
7. Click **"Add User"**

**IMPORTANT**: Save these credentials:
- Username: `allflex_user`
- Password: `YOUR_GENERATED_PASSWORD`

### 4. Configure Network Access
1. Go to **Network Access** (left sidebar under Security)
2. Click **"Add IP Address"**
3. For development: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
4. For production: Add your specific server IP
5. Click **"Confirm"**

### 5. Get Connection String
1. Go to **Database** (left sidebar)
2. Click **"Connect"** on your cluster
3. Select **"Drivers"**
4. Driver: **Python**
5. Version: **3.12 or later**
6. Copy the connection string (looks like):
   ```
   mongodb+srv://allflex_user:<password>@allflex-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### 6. Prepare Connection String
Replace `<password>` with your actual password:
```
mongodb+srv://allflex_user:YOUR_ACTUAL_PASSWORD@allflex-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=AllFlex
```

**Extract these values for .env:**
- `MONGO_DB_HOST`: `allflex-cluster.xxxxx.mongodb.net`
- `MONGO_DB_NAME`: `allflex_db` (you'll create this)
- `MONGO_DB_USER`: `allflex_user`
- `MONGO_DB_PASSWORD`: `YOUR_ACTUAL_PASSWORD`

### 7. Install Python Packages
```bash
pip install -r requirements.txt
```

### 8. Create Database
MongoDB creates databases automatically on first write. Your database `allflex_db` will be created when you first save a document.

You can verify in Atlas:
1. Go to **Database** → **Browse Collections**
2. After running your app, you'll see `allflex_db` listed

---

## Connection String Format

**Full Connection String:**
```
mongodb+srv://<username>:<password>@<cluster-url>/<database>?retryWrites=true&w=majority&appName=AllFlex
```

**Example:**
```
mongodb+srv://allflex_user:MyP@ssw0rd123@allflex-cluster.abc123.mongodb.net/allflex_db?retryWrites=true&w=majority&appName=AllFlex
```

---

## Security Best Practices

1. **Never commit credentials to Git**
   - Always use `.env` file
   - Add `.env` to `.gitignore`

2. **Use strong passwords**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols

3. **Restrict IP Access in Production**
   - Don't use 0.0.0.0/0 in production
   - Add only your server's IP address

4. **Enable MongoDB Atlas Alerts**
   - Set up email alerts for unusual activity
   - Monitor connection spikes

5. **Regular Backups**
   - MongoDB Atlas provides automatic backups (paid tiers)
   - Export important data regularly

---

## Troubleshooting

### Connection Timeout
- Check network access (IP whitelist)
- Verify credentials
- Check if cluster is paused (free tier pauses after inactivity)

### Authentication Failed
- Double-check username/password
- Ensure password doesn't have special characters that need URL encoding
- URL encode password if needed: `@` → `%40`, `#` → `%23`

### Database Not Showing
- MongoDB creates database on first write operation
- Run signup/create user first
- Refresh Atlas dashboard

---

## Next Steps

After setup:
1. Update `.env` with MongoDB credentials
2. Run migrations (see MIGRATION_GUIDE.md)
3. Test authentication
4. Verify data in Atlas dashboard
