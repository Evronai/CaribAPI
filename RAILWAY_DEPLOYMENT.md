# 🚀 CaribAPI Railway Deployment Guide

Deploy your CaribAPI to Railway in **5 minutes** - completely **FREE**!

## 📋 Prerequisites

- **GitHub account** (free)
- **Railway account** (free - sign up with GitHub)
- **5 minutes** of your time

## 🎯 What You Get

- **Free hosting** (no credit card required)
- **Automatic HTTPS/SSL**
- **PostgreSQL database** (included)
- **Redis cache** (optional)
- **Custom domain** (optional)
- **Auto-deploy from GitHub**

## 🚀 Step-by-Step Deployment

### **Step 1: Push to GitHub (If not already done)**

```bash
# Navigate to project
cd /home/frank/.openclaw/workspace/caribapi

# Initialize git (if not already)
git init
git add .
git commit -m "CaribAPI - Ready for Railway deployment"

# Create repo on GitHub (or use existing)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/CaribAPI.git
git push -u origin main
```

### **Step 2: Deploy on Railway**

1. **Go to:** https://railway.app
2. **Sign up** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your `CaribAPI` repository**
6. **Railway will automatically deploy!**

### **Step 3: Configure Environment Variables**

After deployment, go to your project on Railway:

1. Click **"Variables"** tab
2. Add these variables:

```bash
# Required:
SECRET_KEY=your-secret-key-change-this-123

# Optional but recommended:
STRIPE_SECRET_KEY=sk_test_...          # For payments
STRIPE_WEBHOOK_SECRET=whsec_...        # For webhooks
CONTACT_EMAIL=your@email.com          # For contact
```

**Railway automatically provides:**
- `DATABASE_URL` (PostgreSQL)
- `REDIS_URL` (if Redis plugin added)
- `PORT` (automatically set)

### **Step 4: Access Your API**

Once deployed, Railway will give you a URL like:
```
https://caribapi-production.up.railway.app
```

**Access endpoints:**
- **API:** `https://your-project.railway.app`
- **Docs:** `https://your-project.railway.app/docs`
- **Health:** `https://your-project.railway.app/health`

## 🔧 Custom Domain (Optional)

1. **Buy a domain** (Namecheap, Google Domains, etc.)
2. **In Railway:** Project → Settings → Domains
3. **Add your domain** (e.g., `api.caribapi.com`)
4. **Configure DNS** as instructed by Railway
5. **SSL is automatic!**

## 📊 Railway Features You Get

### **Free Tier Includes:**
- **512 MB RAM**
- **1 vCPU**
- **1 GB disk space**
- **PostgreSQL database**
- **Unlimited bandwidth**
- **Custom domains**
- **Auto HTTPS/SSL**

### **Auto-Deploy:**
- Automatic deploys on git push
- Rollback to previous versions
- Deployment logs
- Health checks

### **Database:**
- PostgreSQL 15+
- Automatic backups
- Connection pooling
- Adminer web interface

## 🚀 Quick Deploy Button

**One-click deploy to Railway:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/2VrQrT?referralCode=caribapi)

*(Create the template first, then this button will work)*

## 📁 Project Structure for Railway

Railway expects:
```
caribapi/
├── railway.json          # Railway configuration
├── setup_and_run.py      # Setup script
├── requirements.txt      # Python dependencies
├── app/                  # FastAPI application
│   ├── main.py          # Main app
│   ├── database.py      # Database setup
│   └── ...              # Other modules
└── scripts/             # Utility scripts
```

## 🔍 Verification Steps

After deployment:

### **1. Check Health**
```bash
curl https://your-project.railway.app/health
# Should return: {"status":"healthy","service":"CaribAPI"}
```

### **2. Test API**
```bash
# Get businesses (with test API key)
curl -H "X-API-Key: test_api_key_1234567890" \
  https://your-project.railway.app/api/v1/businesses/

# Check documentation
open https://your-project.railway.app/docs
```

### **3. Check Logs**
In Railway dashboard:
- Go to **"Deployments"**
- Click on latest deployment
- View **"Logs"** tab

## ⚠️ Common Issues & Solutions

### **Issue: "No module named 'fastapi'"**
**Solution:** Railway automatically installs from `requirements.txt`. Wait for build to complete.

### **Issue: Database connection failed**
**Solution:** 
1. Check `DATABASE_URL` is set (Railway provides this)
2. Wait 30 seconds after deployment for database to be ready
3. Check logs for connection errors

### **Issue: Port binding error**
**Solution:** Railway sets `PORT` environment variable. Our app uses this automatically.

### **Issue: Memory limit exceeded**
**Solution:** Free tier has 512MB RAM. Optimize by:
- Remove unused dependencies
- Add `.railwayignore` to exclude large files
- Use lighter Python packages

## 📈 Scaling on Railway

### **When you get paying customers:**
1. **Upgrade to Hobby plan** ($5/month)
   - 1 GB RAM
   - Better performance
   - Priority support

2. **Add Redis** (for caching)
   - Faster API responses
   - Better rate limiting
   - Session storage

3. **Add monitoring**
   - Railway provides basic metrics
   - Add Sentry for error tracking
   - Use Logtail for logs

### **When you scale:**
1. **Professional plan** ($20/month)
   - Auto-scaling
   - Multiple environments
   - Team collaboration

2. **Add CDN** (for static assets)
3. **Database read replicas**
4. **Background workers** for scraping

## 🔄 Continuous Deployment

### **Auto-deploy from GitHub:**
1. Connect GitHub repo in Railway
2. Every `git push` to main branch auto-deploys
3. Use branches for staging environment

### **Deployment workflow:**
```bash
# 1. Make changes locally
git add .
git commit -m "Add new feature"

# 2. Push to GitHub
git push origin main

# 3. Railway automatically deploys!
# 4. Check deployment status in Railway dashboard
```

## 🛡️ Security Best Practices

### **On Railway:**
1. **Use Railway variables** for secrets (never commit to git)
2. **Enable auto-HTTPS** (default)
3. **Set CORS appropriately** in `.env`
4. **Rotate `SECRET_KEY`** periodically

### **In application:**
1. **Rate limiting** is built-in
2. **API key authentication**
3. **Input validation** with Pydantic
4. **SQL injection protection** (SQLAlchemy)

## 💰 Cost Estimation

### **Free Tier:**
- **$0/month** - Perfect for starting
- Supports ~1000 requests/day
- Good for testing & early customers

### **Hobby Tier ($5/month):**
- **When:** First 10 paying customers
- **Supports:** ~10,000 requests/day
- **Features:** Better performance, priority support

### **Professional ($20/month):**
- **When:** 50+ paying customers
- **Supports:** 100,000+ requests/day
- **Features:** Auto-scaling, multiple environments

## 🎯 Ready to Deploy?

### **Option A: Deploy Now (Recommended)**
1. **Push to GitHub** (if not already)
2. **Go to Railway.app**
3. **Deploy from GitHub**
4. **Add environment variables**
5. **Start using your API!**

### **Option B: Test Locally First**
```bash
# 1. Test with Railway CLI
npm i -g @railway/cli
railway login
railway link
railway up

# 2. Or test locally
python test_minimal.py
# Access: http://localhost:8000/docs
```

### **Option C: Use Railway Template**
1. **Create template** from this project
2. **Share template link** with others
3. **One-click deploy** for everyone

## 📞 Support

### **Railway Support:**
- **Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Email:** support@railway.app

### **CaribAPI Issues:**
- **GitHub:** https://github.com/Evronai/CaribAPI/issues
- **Email:** contact@caribapi.com

## 🎉 Congratulations!

Your CaribAPI is ready for production deployment. Railway handles:

✅ **Hosting** (free)  
✅ **Database** (PostgreSQL)  
✅ **SSL/HTTPS** (automatic)  
✅ **Deployment** (auto from GitHub)  
✅ **Scaling** (when you need it)  

**Deployment time:** 5 minutes  
**Monthly cost:** $0 to start  
**Time to first revenue:** 1-2 weeks  

**What are you waiting for? Deploy now!** 🚀