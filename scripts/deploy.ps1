# Deployment script for Windows
# Usage: .\scripts\deploy.ps1

Write-Host "================================"
Write-Host "🚀 ECOME FINANCE DEPLOYMENT"
Write-Host "================================"
Write-Host ""

# Check Python
Write-Host "✓ Checking Python..."
python --version

# Check virtual environment
Write-Host "✓ Checking virtual environment..."
if (Test-Path ".\.venv") {
    Write-Host "✓ Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠ Virtual environment not found. Create with: python -m venv .venv"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env if missing
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚠ .env file not found. Creating from .env.example..."
    Copy-Item ".env.example" ".env"
    Write-Host "⚠ Please edit .env with your configuration before continuing"
    exit 1
}

# Run Django checks
Write-Host ""
Write-Host "🔍 Running Django checks..."
python manage.py check

# Apply migrations
Write-Host ""
Write-Host "🔄 Applying migrations..."
python manage.py migrate

# Collect static files
Write-Host ""
Write-Host "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create default data (optional)
Write-Host ""
$response = Read-Host "Create test data? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    python manage.py shell < scripts\create_test_data.py
}

Write-Host ""
Write-Host "================================"
Write-Host "✅ DEPLOYMENT COMPLETE!"
Write-Host "================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the .env file configuration"
Write-Host "2. Test the application: python manage.py runserver"
Write-Host "3. Access admin at: http://localhost:8000/admin"
Write-Host "   Username: admin | Password: admin"
Write-Host ""
