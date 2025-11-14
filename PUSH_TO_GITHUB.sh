#!/bin/bash

echo "=== Pushing Monte Carlo Options Pricer to GitHub ==="
echo ""

# Set your git identity (replace with your email if needed)
echo "Setting git identity..."
git config user.name "Siddharth Nandakumar"
git config user.email "siddharth@example.com"  # Update this with your actual email
echo "✓ Git identity set to: Siddharth Nandakumar"
echo ""

# 1. Initialize git if not already done
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# 2. Add all files
echo ""
echo "Adding all files..."
git add .

# 3. Create initial commit (ONLY with your name)
echo ""
echo "Creating commit..."
git commit -m "Initial implementation of Monte Carlo Options Pricer

Features:
- Black-Scholes and Heston stochastic volatility models
- European and exotic options (Asian, Barrier, Lookback, Digital)
- Variance reduction techniques (antithetic, control variates, quasi-random)
- FastAPI web application with interactive frontend
- Comprehensive test suite and benchmarking tools
- Docker deployment configuration

Tech stack: Python, NumPy, SciPy, FastAPI, Docker"

# 4. Add remote
echo ""
echo "Adding GitHub remote..."
git remote add origin https://github.com/SiddNan/Monte-Carlo-Options-Pricer.git 2>/dev/null || echo "Remote already exists"

# 5. Set main branch
echo ""
echo "Setting main branch..."
git branch -M main

# 6. Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "=== ✓ Successfully pushed to GitHub! ==="
echo ""
echo "Repository: https://github.com/SiddNan/Monte-Carlo-Options-Pricer"
echo "Author: Siddharth Nandakumar"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app to deploy"
echo "2. Or visit https://render.com for alternative deployment"
echo "3. Update README with your live URL once deployed"
echo ""
echo "IMPORTANT: Verify your commit author with:"
echo "  git log --format='%an <%ae>' -n 1"
