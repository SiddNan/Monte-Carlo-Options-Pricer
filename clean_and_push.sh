#!/bin/bash

echo "=== Cleaning Repository & Pushing Clean Version ==="
echo ""

# Remove meta files from git tracking
echo "1. Removing helper/meta files from git..."
git rm --cached AI_DETECTION_CHECKLIST.md FINAL_CHECKLIST.md verify_before_push.sh fix_and_push.sh fix_author.sh PUSH_TO_GITHUB.sh PROJECT_STATUS.md QUICK_DEPLOY.md START_HERE.md DEPLOYMENT_STEPS.md 2>/dev/null
echo "   ✓ Meta files removed from tracking"
echo ""

# Add updated .gitignore
echo "2. Updating .gitignore..."
git add .gitignore
echo "   ✓ .gitignore updated"
echo ""

# Commit the cleanup
echo "3. Creating cleanup commit..."
git commit -m "Remove helper scripts and meta documentation

Cleaned up repository to include only project code and essential documentation.
Removed internal helper scripts and checklists."

if [ $? -eq 0 ]; then
    echo "   ✓ Cleanup committed"
else
    echo "   (No changes to commit)"
fi
echo ""

# Push
echo "4. Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=== ✅ Repository Cleaned! ==="
    echo ""
    echo "Repository now contains only:"
    echo "  ✓ Source code (src/mc_pricer/)"
    echo "  ✓ Tests (tests/)"
    echo "  ✓ Examples (examples/)"
    echo "  ✓ API (api/)"
    echo "  ✓ Essential docs (README.md, SUMMARY.md, DEPLOYMENT.md)"
    echo "  ✓ Deployment configs (Dockerfile, docker-compose.yml, etc.)"
    echo ""
    echo "Removed:"
    echo "  ✗ Helper scripts"
    echo "  ✗ Internal checklists"
    echo "  ✗ Meta documentation"
    echo ""
    echo "View clean repo: https://github.com/SiddNan/Monte-Carlo-Options-Pricer"
else
    echo ""
    echo "⚠️ Push failed"
fi
