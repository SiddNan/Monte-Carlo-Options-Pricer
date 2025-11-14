#!/bin/bash

echo "=== Pre-Push Verification ==="
echo ""

# Check 1: Git identity
echo "1. Checking git identity..."
NAME=$(git config user.name 2>/dev/null || echo "NOT SET")
EMAIL=$(git config user.email 2>/dev/null || echo "NOT SET")

if [[ "$NAME" == "Siddharth Nandakumar" ]]; then
    echo "   ✓ Name: $NAME"
else
    echo "   ✗ Name: $NAME (should be 'Siddharth Nandakumar')"
    echo "   Run: git config user.name 'Siddharth Nandakumar'"
fi

if [[ "$EMAIL" != *"anthropic"* && "$EMAIL" != *"claude"* ]]; then
    echo "   ✓ Email: $EMAIL"
else
    echo "   ✗ Email contains AI reference: $EMAIL"
    echo "   Run: git config user.email 'your-email@example.com'"
fi
echo ""

# Check 2: No Claude/AI references in code
echo "2. Checking for AI references in code..."
if grep -r "Claude\|Anthropic\|noreply@anthropic" src/ examples/ api/ --include="*.py" 2>/dev/null; then
    echo "   ✗ Found AI references in code!"
else
    echo "   ✓ No AI references in source code"
fi
echo ""

# Check 3: Author attribution
echo "3. Checking author in setup.py..."
if grep -q "Siddharth Nandakumar" setup.py; then
    echo "   ✓ Author set correctly in setup.py"
else
    echo "   ✗ Author not set in setup.py"
fi
echo ""

# Check 4: Repository URL
echo "4. Checking repository URL..."
if grep -q "SiddNan/Monte-Carlo-Options-Pricer" setup.py; then
    echo "   ✓ GitHub URL correct in setup.py"
else
    echo "   ✗ GitHub URL not set correctly"
fi
echo ""

# Check 5: Test imports
echo "5. Testing imports..."
cd "$(dirname "$0")"
if python3 -c "import sys; sys.path.insert(0, 'src'); from mc_pricer import MonteCarloEngine; print('   ✓ Imports work')" 2>/dev/null; then
    :
else
    echo "   ✗ Import test failed"
fi
echo ""

echo "=== Verification Complete ==="
echo ""
echo "If all checks passed, you're ready to push!"
echo "Run: ./PUSH_TO_GITHUB.sh"
