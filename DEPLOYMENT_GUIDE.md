# CaribAPI Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Railway.app (Free, Recommended)
1. **Visit:** https://railway.app
2. **Sign up** with GitHub
3. **Click "New Project"** → "Deploy from GitHub repo"
4. **Select** `Evronai/CaribAPI`
5. **Add variables:**
   - `DATABASE_URL` (Railway will auto-create PostgreSQL)
   - `REDIS_URL` (Railway will auto-create Redis)
   - `SECRET_KEY` (generate random string)
   - `STRIPE_SECRET_KEY` (get from Stripe dashboard)
   - `STRIPE_WEBHOOK_SECRET` (get from Stripe)
6. **Deploy!** - Your API will be live in 2 minutes

### Option 2: Render.com (Free)
1. **Visit:** https://render.com
2. **Sign up** with GitHub
3. **Click "New +"** → "Web Service"
4. **Connect** to `Evronai/CaribAPI`
5. **Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Add environment variables** (same as Railway)
7. **Create database:** Add PostgreSQL add-on
8. **Deploy!**

### Option 3: DigitalOcean ($5/month, Most Reliable)
```bash
# 1. Create Droplet (Ubuntu 22.04, $5/month)
# 2. SSH into server
ssh root@your-server-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose

# 5. Clone repository
git clone https://github.com/Evronai/CaribAPI.git
cd CaribAPI

# 6. Create .env file
cp .env.example .env
nano .env  # Edit with your values

# 7. Start services
docker-compose up -d

# 8. Create sample data
docker-compose exec api python scripts/create_sample_data.py
```

## 🌐 Domain Setup

### Custom Domain (Optional)
1. **Buy domain:** Namecheap, Google Domains ($10-15/year)
2. **Point to Railway/Render:** Add CNAME record
3. **SSL:** Automatic with Railway/Render

### Free Subdomain
- Railway: `your-project.railway.app`
- Render: `your-project.onrender.com`

## 🔧 Environment Variables

### Required:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port
SECRET_KEY=your-secret-key-change-this
```

### For Payments (Optional but recommended):
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...  # $49/month price ID
STRIPE_PRICE_BUSINESS=price_...  # $199/month price ID
```

## 📊 Database Setup

### Railway/Render (Auto-provisioned):
- PostgreSQL database automatically created
- Redis cache automatically created
- Connection strings injected as environment variables

### Manual Setup:
```sql
-- Create database
CREATE DATABASE caribapi;

-- Create user
CREATE USER caribapi WITH PASSWORD 'your-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE caribapi TO caribapi;
```

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl https://your-api.railway.app/health
# Should return: {"status":"healthy","service":"CaribAPI"}
```

### 2. API Documentation
Visit: `https://your-api.railway.app/docs`

### 3. Test Endpoints
```bash
# Get businesses (with test API key)
curl -H "X-API-Key: test_api_key_1234567890" \
  https://your-api.railway.app/api/v1/businesses/

# Search businesses
curl -H "X-API-Key: test_api_key_1234567890" \
  "https://your-api.railway.app/api/v1/businesses/search?q=brewery"
```

## 🔐 Security Checklist

### Before Going Live:
- [ ] Change `SECRET_KEY` to random string
- [ ] Remove test API keys from sample data
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Set up monitoring/alerting
- [ ] Backup database regularly

### Production Recommendations:
- **Use HTTPS only**
- **Enable API key rotation**
- **Monitor usage patterns**
- **Set up logging**
- **Regular security updates**

## 📈 Scaling

### Small (0-100 users):
- Railway/Render free tier
- Basic monitoring
- Manual backups

### Medium (100-1000 users):
- DigitalOcean $10-20/month
- Automated backups
- Basic monitoring (UptimeRobot)

### Large (1000+ users):
- AWS/GCP $50-200/month
- Load balancing
- Advanced monitoring (Datadog, New Relic)
- CDN for static assets

## 🆘 Troubleshooting

### Common Issues:

1. **Database connection failed**
   ```bash
   # Check if database is running
   # Verify DATABASE_URL format
   # Check firewall rules
   ```

2. **API not responding**
   ```bash
   # Check logs: railway logs or docker-compose logs
   # Verify port binding
   # Check memory/CPU usage
   ```

3. **Rate limiting too aggressive**
   ```bash
   # Adjust RATE_LIMIT_* variables
   # Consider user's plan when setting limits
   ```

### Getting Help:
- Check application logs
- Test locally first
- Use `scripts/test_api.py`
- Consult API documentation

## 🚀 Next Steps After Deployment

### Week 1:
1. **Test all endpoints**
2. **Add real business data** (scrape Trinidad registry)
3. **Set up Stripe** for payments
4. **Create landing page** (caribapi.com)

### Month 1:
1. **Add more Caribbean countries**
2. **Implement webhooks**
3. **Build customer dashboard**
4. **Start marketing**

### Month 3:
1. **Add machine learning insights**
2. **Real-time data updates**
3. **Partner integrations**
4. **Mobile app**

## 📞 Support

- **GitHub Issues:** https://github.com/Evronai/CaribAPI/issues
- **Email:** contact@caribapi.com
- **Documentation:** https://your-api.railway.app/docs

---

**Your CaribAPI is now ready to make money!** 🎉

Start by:
1. Deploying to Railway (free)
2. Adding real Trinidad business data
3. Setting up Stripe payments
4. Marketing to Caribbean developers

Expected timeline to first revenue: **1-2 weeks**