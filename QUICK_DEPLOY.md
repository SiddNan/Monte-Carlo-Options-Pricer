# 🚀 Quick Deployment Guide

## ✅ Prerequisites Checked
- ✅ Code is working (tested successfully!)
- ✅ Encoding issues fixed
- ✅ Dependencies listed in requirements.txt
- ✅ Dockerfile and docker-compose ready
- ✅ Deployment configs created

## 🎯 3 Easiest Deployment Options

### Option 1: Railway (RECOMMENDED - 5 minutes)

**Why Railway?**
- Free tier (perfect for portfolio)
- Easiest deployment
- Great for showing to employers
- Auto-generates URL

**Steps:**

1. **Init Git (if not already)**
   ```bash
   cd "/Users/siddharthnandakumar/Desktop/Personal Projects/MC_Options_Pricer"
   git init
   git add .
   git commit -m "Initial commit: Monte Carlo Options Pricer"
   ```

2. **Push to GitHub**
   ```bash
   # Create repo on GitHub first, then:
   git remote add origin https://github.com/YOUR_USERNAME/mc-options-pricer.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy to Railway**
   - Go to https://railway.app
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your `mc-options-pricer` repo
   - Railway auto-detects Dockerfile and deploys!
   - Get your URL: `https://your-app.railway.app`

**That's it!** ✅

---

### Option 2: Render (Also Easy - 5 minutes)

1. Push to GitHub (same as above)
2. Go to https://render.com
3. Click "New Web Service"
4. Connect GitHub repo
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
6. Click "Create Web Service"

---

### Option 3: Local Docker (Test First)

**Test locally before cloud deployment:**

```bash
# Build and run
docker-compose up

# Visit: http://localhost:8000
```

---

## 🧪 Test Your Deployment

Once deployed, test the API:

```bash
# Replace with your deployed URL
curl -X POST "https://your-app.railway.app/price" \
  -H "Content-Type: application/json" \
  -d '{
    "S0": 100,
    "K": 100,
    "T": 1.0,
    "r": 0.05,
    "q": 0.0,
    "sigma": 0.2,
    "option_type": "call",
    "n_paths": 10000,
    "n_steps": 100,
    "variance_reduction": "antithetic"
  }'
```

Or just visit the URL in your browser!

---

## 📝 Add to Resume/LinkedIn

```
Monte Carlo Options Pricer
• Built professional-grade options pricing library with Black-Scholes and Heston models
• Implemented 5 variance reduction techniques (40-80% variance reduction)
• Deployed interactive web application for real-time pricing
• Live demo: https://your-app.railway.app

Tech: Python, NumPy, SciPy, FastAPI, Docker
```

---

## 🎤 For Interviews

When showing this project:

1. **Start with the live demo** - Show it working in real-time
2. **Explain the math** - Risk-neutral pricing, variance reduction theory
3. **Show the code** - Clean architecture, proper OOP, type hints
4. **Discuss performance** - O(1/√N) convergence, vectorization
5. **Talk about next steps** - American options, GPU acceleration, etc.

---

## 🐛 Troubleshooting

**Port issues?**
- Railway/Render automatically set `$PORT` environment variable

**Dependencies?**
- All listed in requirements.txt
- Docker installs them automatically

**API not responding?**
- Check logs in Railway/Render dashboard
- Verify FastAPI is running on `0.0.0.0:$PORT`

---

## 🎉 You're Ready!

Your Monte Carlo Options Pricer is production-ready and deployable. This is exactly the kind of project that impresses quant firms!

**Next Steps:**
1. Deploy to Railway (5 min)
2. Add URL to your resume
3. Share on LinkedIn
4. Use in interviews

Good luck! 🚀
