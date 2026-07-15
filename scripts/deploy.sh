#!/bin/bash

# Deployment script for manual deployment
# Usage: ./scripts/deploy.sh

set -e  # Exit on error

echo "================================"
echo "🚀 ECOME FINANCE DEPLOYMENT"
echo "================================"
echo ""

# Check Python
echo "✓ Checking Python..."
python --version

# Check virtual environment
echo "✓ Checking virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Virtual environment not found. Create with: python -m venv .venv"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠ Please edit .env with your configuration before continuing"
    exit 1
fi

# Run Django checks
echo ""
echo "🔍 Running Django checks..."
python manage.py check

# Apply migrations
echo ""
echo "🔄 Applying migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create default data (optional)
echo ""
read -p "Create test data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py shell < scripts/create_test_data.py
fi

echo ""
echo "================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Review the .env file configuration"
echo "2. Test the application: python manage.py runserver"
echo "3. Access admin at: http://localhost:8000/admin"
echo "   Username: admin | Password: admin"
echo ""
