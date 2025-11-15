#!/bin/bash

echo "=== Final Repository Cleanup ==="
echo ""

# Remove all meta/helper files from git
echo "Removing meta files from repository..."
git rm AI_DETECTION_CHECKLIST.md FINAL_CHECKLIST.md PROJECT_STATUS.md QUICK_DEPLOY.md START_HERE.md DEPLOYMENT_STEPS.md 2>/dev/null
git rm verify_before_push.sh fix_and_push.sh fix_author.sh PUSH_TO_GITHUB.sh clean_and_push.sh 2>/dev/null

echo "✓ Removed from git"
echo ""

# Commit removal
echo "Committing cleanup..."
git commit -m "Clean repository - remove internal documentation and helper scripts"

echo ""
echo "Pushing to GitHub..."
git push origin main

echo ""
echo "=== ✅ Done! ==="
echo ""
echo "Repository now contains only essential project files."
echo "View at: https://github.com/SiddNan/Monte-Carlo-Options-Pricer"
