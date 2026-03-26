# CaribAPI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Simple Launch (Recommended)
```bash
# 1. Clone or navigate to caribapi directory
cd caribapi

# 2. Make launch script executable
chmod +x launch.sh

# 3. Launch the API
./launch.sh
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Create sample data
python scripts/create_sample_data.py

# 4. Start the API
uvicorn app.main:app --reload
```

## 📡 API Access

Once running, access:
- **API Documentation:** http://localhost:8000/docs
- **API Root:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

## 🔑 Authentication

Use the test API key: `test_api_key_1234567890`

Add to requests as header:
```bash
curl -H "X-API-Key: test_api_key_1234567890" \
  http://localhost:8000/api/v1/businesses/
```

## 📊 Sample Endpoints

### Get Businesses
```bash
GET /api/v1/businesses/
GET /api/v1/businesses/?city=Port%20of%20Spain
GET /api/v1/businesses/?industry=Technology
```

### Search Businesses
```bash
GET /api/v1/businesses/search?q=brewery
GET /api/v1/businesses/search?q=construction&city=San%20Fernando
```

### Get Business by ID
```bash
GET /api/v1/businesses/1
GET /api/v1/businesses/registration/TRN20240001
```

### Statistics
```bash
GET /api/v1/businesses/stats/summary
```

## 💰 Business Model

### Pricing Plans
| Plan | Monthly Price | Requests/Day | Requests/Month | Features |
|------|---------------|--------------|----------------|----------|
| Free | $0 | 100 | 3,000 | Basic access, Trinidad data only |
| Pro | $49 | 10,000 | 300,000 | All Caribbean countries, API support |
| Business | $199 | 100,000 | 3,000,000 | Webhooks, Priority support, Custom data |

### Expected Revenue
- **Month 1:** $0-500 (beta users)
- **Month 3:** $1,000-2,000
- **Month 6:** $5,000+
- **Month 12:** $10,000+

## 🎯 Target Customers

1. **Caribbean Fintech Startups** - KYC/AML compliance
2. **Local Government Agencies** - Business intelligence
3. **International Corporations** - Market entry research
4. **Research Institutions** - Economic studies
5. **Real Estate Developers** - Market analysis

## 🔧 Technology Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Cache:** Redis
- **Payments:** Stripe
- **Hosting:** DigitalOcean/Linode
- **Monitoring:** Sentry + Logging

## 🚀 Deployment

### DigitalOcean (Recommended)
```bash
# 1. Create Droplet
# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Install Docker Compose
sudo apt-get install docker-compose

# 4. Deploy
git clone https://github.com/yourusername/caribapi.git
cd caribapi
docker-compose up -d
```

### Heroku
```bash
# 1. Create Heroku app
heroku create caribapi

# 2. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 3. Add Redis
heroku addons:create heroku-redis:hobby-dev

# 4. Deploy
git push heroku main
```

## 📈 Next Steps

### Phase 1: MVP (Week 1)
- [x] Basic API with Trinidad business data
- [x] Authentication & rate limiting
- [x] Sample data & documentation
- [ ] Stripe integration for payments
- [ ] Basic dashboard for users

### Phase 2: Growth (Month 1)
- [ ] Add more Caribbean countries
- [ ] Advanced search filters
- [ ] Data export (CSV, Excel)
- [ ] Webhook support
- [ ] API usage analytics

### Phase 3: Scale (Month 3)
- [ ] Machine learning insights
- [ ] Real-time data updates
- [ ] Partner integrations
- [ ] Mobile app
- [ ] Enterprise features

## 🆘 Troubleshooting

### Common Issues

1. **Database connection failed**
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Update DATABASE_URL in .env
   ```

2. **Port 8000 already in use**
   ```bash
   # Change port
   uvicorn app.main:app --port 8001 --reload
   ```

3. **Missing dependencies**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

### Getting Help
- Check logs: `docker-compose logs api`
- Test API: `python scripts/test_api.py`
- Visit docs: http://localhost:8000/docs

## 📄 License

MIT License - Free to use and modify for commercial purposes.

## 🤝 Contributing

Want to help improve CaribAPI?
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🚀 Production Deployment

### One-Click Deploy:
- **Render:** [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/CaribAPI)
- **Railway:** [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?template=https://github.com/Evronai/CaribAPI)

### Detailed Guides:
- [Render Deployment](RENDER_DEPLOYMENT.md)
- [Railway Deployment](RAILWAY_DEPLOYMENT.md)
- [Deploy Now](DEPLOY_NOW.md)

## 📞 Contact

For questions or support:
- Email: contact@caribapi.com
- GitHub Issues: https://github.com/yourusername/caribapi/issues
- Documentation: https://docs.caribapi.com

---

**Built with ❤️ for the Caribbean business community**