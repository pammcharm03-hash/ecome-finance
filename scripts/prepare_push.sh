#!/bin/bash

# GitHub Push Preparation Script
# Ensures everything is ready before pushing to GitHub

echo "================================"
echo "📤 GITHUB PUSH PREPARATION"
echo "================================"
echo ""

# Check git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git config user.email "developer@ecome-finance.local"
    git config user.name "ECOME Developer"
fi

# Check .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file before pushing"
    exit 1
fi

# Check .env.example exists
if [ ! -f ".env.example" ]; then
    echo "⚠️  .env.example not found. Creating from .env..."
    cp .env .env.example
    # Remove sensitive data from example
    sed -i 's/=.*/=YOUR_VALUE_HERE/g' .env.example
fi

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    echo "Creating requirements.txt..."
    pip freeze > requirements.txt
fi

# Check .gitignore
if [ ! -f ".gitignore" ]; then
    echo "⚠️  .gitignore not found"
fi

# Run Django checks
echo ""
echo "🔍 Running Django checks..."
python manage.py check
if [ $? -ne 0 ]; then
    echo "❌ Django check failed!"
    exit 1
fi

# Check migrations
echo ""
echo "🔄 Checking migrations..."
python manage.py makemigrations --dry-run
if [ $? -ne 0 ]; then
    echo "⚠️  Migration issues detected"
fi

# Show git status
echo ""
echo "📊 Git Status:"
git status

# Ask for confirmation
echo ""
echo "================================"
echo "Ready to push?"
echo "================================"
read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Commit
echo ""
echo "📝 Committing changes..."
read -p "Commit message: " commit_msg
git add .
git commit -m "$commit_msg"

# Check remote
echo ""
echo "🔗 Checking GitHub remote..."
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  No remote repository set"
    echo "Usage: git remote add origin https://github.com/username/repo.git"
    exit 1
fi

# Push
echo ""
echo "📤 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ PUSH SUCCESSFUL!"
    echo "================================"
    echo ""
    echo "GitHub Actions will now:"
    echo "1. Run tests and checks"
    echo "2. Clean database"
    echo "3. Preserve admin/admin credentials"
    echo "4. Run migrations"
    echo "5. Deploy to production"
    echo ""
    echo "Monitor: https://github.com/username/repo/actions"
else
    echo ""
    echo "❌ Push failed!"
    exit 1
fi
