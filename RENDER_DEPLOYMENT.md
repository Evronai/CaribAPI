# 🚀 CaribAPI Render Deployment Guide

Deploy your CaribAPI to Render in **5 minutes** - completely **FREE**!

## 📋 Prerequisites

- **GitHub account** (free)
- **Render account** (free - sign up with GitHub)
- **5 minutes** of your time

## 🎯 What You Get

- **Free hosting** (no credit card required)
- **Automatic HTTPS/SSL**
- **PostgreSQL database** (included)
- **Redis cache** (optional)
- **Custom domain** (optional)
- **Auto-deploy from GitHub**
- **Cron jobs** for scheduled tasks

## 🚀 Step-by-Step Deployment

### **Step 1: Push to GitHub (If not already done)**

```bash
# Navigate to project
cd /home/frank/.openclaw/workspace/caribapi

# Initialize git (if not already)
git init
git add .
git commit -m "CaribAPI - Ready for Render deployment"

# Create repo on GitHub (or use existing)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/CaribAPI.git
git push -u origin main
```

### **Step 2: Deploy on Render**

#### **Option A: One-Click Deploy (Easiest)**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/CaribAPI)

1. **Click the button above** (after updating with your repo URL)
2. **Sign in with GitHub**
3. **Render automatically configures everything** from `render.yaml`
4. **Wait 2-3 minutes** for deployment
5. **Your API is live!** 🎉

#### **Option B: Manual Setup**

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. **Click "New +"** → **"Blueprint"**
4. **Connect your GitHub repository** (CaribAPI)
5. **Render will detect `render.yaml`** and configure services automatically
6. **Click "Apply"** to deploy

### **Step 3: Configure Environment Variables (Optional)**

Render automatically sets up:
- `DATABASE_URL` (from PostgreSQL service)
- `PORT` (automatically assigned)

You can add additional variables in Render dashboard:
1. Go to your **caribapi** service
2. Click **"Environment"** tab
3. Add variables if needed:

```bash
# Recommended:
SECRET_KEY=your-random-secret-key-here
STRIPE_SECRET_KEY=sk_test_...          # For payments
STRIPE_WEBHOOK_SECRET=whsec_...        # For webhooks
CONTACT_EMAIL=your@email.com          # For contact

# CORS (adjust for production):
ALLOWED_ORIGINS=https://your-frontend.com,https://admin.yourdomain.com
```

### **Step 4: Access Your API**

Once deployed, Render will give you a URL like:
```
https://caribapi.onrender.com
```

**Access endpoints:**
- **API:** `https://your-service.onrender.com`
- **Docs:** `https://your-service.onrender.com/docs`
- **Health:** `https://your-service.onrender.com/health`

## 🔧 Custom Domain (Optional)

1. **Buy a domain** (Namecheap, Google Domains, etc.)
2. **In Render:** Service → Settings → Custom Domain
3. **Add your domain** (e.g., `api.caribapi.com`)
4. **Configure DNS** as instructed by Render
5. **SSL is automatic!**

## 📊 Render Features You Get

### **Free Tier Includes:**
- **512 MB RAM**
- **0.1 vCPU** (shared)
- **PostgreSQL database** (free tier)
- **Unlimited bandwidth**
- **Custom domains**
- **Auto HTTPS/SSL**
- **Cron jobs**

### **Limits (Free Tier):**
- **Web services:** Auto-sleep after 15 minutes of inactivity
- **Database:** 1 GB storage, 10,000 rows
- **Perfect for:** Development, testing, low-traffic production

### **Auto-Deploy:**
- Automatic deploys on git push to main branch
- Manual deploy from other branches
- Deployment logs and rollback
- Health checks

## 🚀 Quick Deploy Button

**One-click deploy to Render:**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/CaribAPI)

*(Replace `YOUR_USERNAME` with your GitHub username)*

## 📁 Project Structure for Render

Render expects:
```
caribapi/
├── render.yaml          # Render blueprint (this file)
├── requirements.txt     # Python dependencies
├── app/                 # FastAPI application
│   ├── main.py         # Main app
│   ├── config.py       # Configuration
│   └── ...             # Other modules
├── scripts/            # Utility scripts
└── Dockerfile          # Optional - for Docker deployment
```

## 🔍 Verification Steps

After deployment:

### **1. Check Health**
```bash
curl https://your-service.onrender.com/health
# Should return: {"status":"healthy","service":"CaribAPI"}
```

### **2. Test API**
```bash
# Get businesses (with test API key)
curl -H "X-API-Key: test_api_key_1234567890" \
  https://your-service.onrender.com/api/v1/businesses/

# Check documentation
open https://your-service.onrender.com/docs
```

### **3. Check Logs**
In Render dashboard:
- Go to your **caribapi** service
- Click **"Logs"** tab
- View real-time deployment and runtime logs

### **4. Verify Database**
```bash
# The database is automatically created and connected
# Check if sample data was loaded by testing API endpoints
```

## ⚠️ Common Issues & Solutions

### **Issue: "Application error" or "Service unavailable"**
**Solution:** 
1. Check **Logs** in Render dashboard
2. Wait 30-60 seconds after deployment (cold start)
3. Free tier services sleep after inactivity - first request may be slow

### **Issue: Database connection failed**
**Solution:** 
1. Check `DATABASE_URL` is set (Render provides this automatically)
2. Wait 1-2 minutes after deployment for database to be ready
3. Check PostgreSQL service status in Render dashboard

### **Issue: "Module not found"**
**Solution:** 
1. Check `requirements.txt` includes all dependencies
2. Check build logs in Render
3. Ensure Python version compatibility (3.8+)

### **Issue: Port binding error**
**Solution:** Render sets `PORT` environment variable. Our app uses `${PORT:-8000}` as fallback.

### **Issue: Memory limit exceeded**
**Solution:** Free tier has 512MB RAM. Optimize by:
- Remove unused dependencies from `requirements.txt`
- Add `.renderignore` to exclude large files
- Use lighter Python packages

## 📈 Scaling on Render

### **When you get paying customers:**
1. **Upgrade to Starter plan** ($7/month)
   - Always awake (no sleeping)
   - 1 GB RAM
   - Better performance

2. **Add Redis** (for caching)
   - Faster API responses
   - Better rate limiting
   - Session storage

3. **Database upgrade**
   - Starter: $7/month (1 GB RAM, 256 GB storage)
   - Standard: $50/month (dedicated resources)

### **When you scale:**
1. **Professional plan** ($25+/month)
   - Dedicated instances
   - Auto-scaling
   - Multiple environments (prod, staging)

2. **Add CDN** (for static assets)
3. **Database read replicas**
4. **Background workers** for data scraping

## 🔄 Continuous Deployment

### **Auto-deploy from GitHub:**
1. Connect GitHub repo in Render
2. Every `git push` to main branch auto-deploys
3. Use branches for staging environment

### **Deployment workflow:**
```bash
# 1. Make changes locally
git add .
git commit -m "Add new feature"

# 2. Push to GitHub
git push origin main

# 3. Render automatically deploys!
# 4. Check deployment status in Render dashboard
```

## 🛡️ Security Best Practices

### **On Render:**
1. **Use Render variables** for secrets (never commit to git)
2. **Enable auto-HTTPS** (default)
3. **Set CORS appropriately** (limit to your domains in production)
4. **Rotate `SECRET_KEY`** periodically

### **In application:**
1. **Rate limiting** is built-in
2. **API key authentication**
3. **Input validation** with Pydantic
4. **SQL injection protection** (SQLAlchemy)

## 💰 Cost Estimation

### **Free Tier:**
- **$0/month** - Perfect for starting
- Supports ~1000 requests/day (when awake)
- Good for testing & early customers
- Services sleep after 15 min inactivity

### **Starter Tier ($7/month):**
- **When:** First 10 paying customers
- **Supports:** ~10,000 requests/day
- **Features:** Always awake, better performance

### **Standard Tier ($25+/month):**
- **When:** 50+ paying customers
- **Supports:** 100,000+ requests/day
- **Features:** Dedicated resources, auto-scaling

## 🎯 Ready to Deploy?

### **Option A: Deploy Now (Recommended)**
1. **Push to GitHub** (if not already)
2. **Go to Render.com**
3. **Deploy from GitHub** (using `render.yaml`)
4. **Add environment variables** (optional)
5. **Start using your API!**

### **Option B: Test Locally First**
```bash
# 1. Test with Render CLI
npm install -g render-cli
render login
render blueprint launch

# 2. Or test locally
python test_minimal.py
# Access: http://localhost:8000/docs
```

### **Option C: Docker Deployment**
1. Render automatically uses `Dockerfile` if present
2. Or use Python build from `requirements.txt`
3. Both work with the `render.yaml` blueprint

## 📞 Support

### **Render Support:**
- **Docs:** https://render.com/docs
- **Discord:** https://render.com/discord
- **Email:** support@render.com

### **CaribAPI Issues:**
- **GitHub:** https://github.com/Evronai/CaribAPI/issues
- **Email:** contact@caribapi.com

## 🎉 Congratulations!

Your CaribAPI is ready for production deployment on Render. Render handles:

✅ **Hosting** (free to start)  
✅ **Database** (PostgreSQL included)  
✅ **SSL/HTTPS** (automatic)  
✅ **Deployment** (auto from GitHub)  
✅ **Scaling** (when you need it)  

**Deployment time:** 5 minutes  
**Monthly cost:** $0 to start  
**Time to first revenue:** 1-2 weeks  

**What are you waiting for? Deploy now!** 🚀