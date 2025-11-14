# 🚀 Quick Deployment Steps

## Step 1: Push to GitHub (2 minutes)

```bash
# Run the automated script
./PUSH_TO_GITHUB.sh
```

**Or manually:**

```bash
# Initialize and commit
git init
git add .
git commit -m "Initial implementation of Monte Carlo Options Pricer"

# Add your repo and push
git remote add origin https://github.com/SiddNan/Monte-Carlo-Options-Pricer.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Railway (3 minutes) - RECOMMENDED

### Why Railway?
- ✅ Free tier (500 hours/month)
- ✅ Auto-detects Dockerfile
- ✅ Free custom domain
- ✅ Perfect for portfolios

### Steps:

1. **Go to https://railway.app**

2. **Click "Start a New Project"**

3. **Choose "Deploy from GitHub repo"**
   - Sign in with GitHub
   - Authorize Railway

4. **Select repository:**
   - Choose `SiddNan/Monte-Carlo-Options-Pricer`

5. **Railway auto-deploys!**
   - Detects Dockerfile
   - Builds and deploys automatically
   - Assigns URL like: `monte-carlo-options-pricer.up.railway.app`

6. **Get your URL:**
   - Click on deployment
   - Copy the public URL
   - Add to your resume!

**Total time: ~3 minutes** ⏱️

---

## Alternative: Deploy to Render (Also Easy)

1. Go to https://render.com
2. Click "New Web Service"
3. Connect GitHub repo: `SiddNan/Monte-Carlo-Options-Pricer`
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

---

## Step 3: Test Your Deployment

Once deployed, test it:

```bash
# Replace YOUR_URL with your actual Railway/Render URL
curl -X POST "https://YOUR_URL/price" \
  -H "Content-Type: application/json" \
  -d '{
    "S0": 100,
    "K": 100,
    "T": 1.0,
    "r": 0.05,
    "sigma": 0.2,
    "option_type": "call",
    "n_paths": 10000,
    "variance_reduction": "antithetic"
  }'
```

Or just visit the URL in your browser!

---

## Step 4: Update Your Resume

```markdown
Monte Carlo Options Pricer | Python, NumPy, FastAPI, Docker
• Developed professional options pricing library with Black-Scholes & Heston models
• Achieved 40-80% variance reduction through advanced techniques
• Built REST API and deployed web application on Railway
• Live Demo: https://your-url.railway.app

GitHub: https://github.com/SiddNan/Monte-Carlo-Options-Pricer
```

---

## Step 5: Share on LinkedIn

```
🚀 Just deployed my Monte Carlo Options Pricer!

Built a production-ready options pricing library with:
✓ Black-Scholes & Heston stochastic volatility models
✓ Variance reduction techniques (40-80% improvement)
✓ Interactive web interface with real-time pricing
✓ Full Docker deployment

Perfect for quant finance roles at market makers and trading firms.

Try it: [your-url]
Code: https://github.com/SiddNan/Monte-Carlo-Options-Pricer

#QuantFinance #Python #MachineLearning #Finance
```

---

## Troubleshooting

**Build fails on Railway?**
- Check Railway logs
- Ensure Dockerfile is present
- Verify requirements.txt is complete

**Port binding error?**
- Railway sets $PORT automatically
- Code already handles this: `--port $PORT`

**Dependencies missing?**
```bash
# Test locally first
pip install -r requirements.txt
python -c "import numpy, scipy, fastapi; print('OK')"
```

---

## Local Testing Before Deploy

```bash
# Option 1: Docker
docker-compose up
# Visit: http://localhost:8000

# Option 2: Direct
source venv/bin/activate
pip install -r requirements.txt
cd api && python main.py
```

---

## Next Steps After Deployment

1. ✅ Add live URL to resume
2. ✅ Share on LinkedIn
3. ✅ Add to portfolio website
4. ✅ Use in job applications
5. ✅ Demo in interviews

**You're ready to impress top quant firms!** 🎯
