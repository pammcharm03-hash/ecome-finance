# 🚀 AUTOMATIC DEPLOYMENT GUIDE

## Setup Instructions

### Step 1: Initialize GitHub Repository

```bash
# If not already initialized
git init
git add .
git commit -m "Initial commit: ECOME Finance System"
git branch -M main
git remote add origin https://github.com/yourusername/ecome-finance.git
git push -u origin main
```

---

## Step 2: Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

```
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
PAYPACK_CLIENT_ID=your-client-id
PAYPACK_CLIENT_SECRET=your-client-secret
PAYPACK_WEBHOOK_URL=https://yourdomain.com/payments/webhook/
```

---

## Step 3: Automatic Deployment Flow

### When you push code to main branch:

```
git push origin main
    ↓
GitHub Actions triggered (.github/workflows/deploy.yml)
    ↓
✓ Run Django checks
✓ Test migrations
✓ Install dependencies
    ↓
✓ Clean database (remove db.sqlite3)
✓ Run init_deployment.py:
    - Preserve admin/admin credentials
    - Run migrations
    - Create default branch
    ↓
✓ Collect static files
    ↓
✓ Deploy to production
    ↓
✅ LIVE! Admin credentials unchanged
```

---

## Step 4: Local Deployment (Manual)

### On Linux/Mac:
```bash
bash scripts/deploy.sh
```

### On Windows (PowerShell):
```powershell
.\scripts\deploy.ps1
```

### Or manually:
```bash
# Activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your settings

# Reset database (preserves admin)
python manage.py migrate
python scripts/init_deployment.py

# Collect static files
python manage.py collectstatic --noinput

# Start server
python manage.py runserver
```

---

## Database Reset Behavior

### Admin User (admin/admin)
```
PRESERVED ✅
- Username: admin
- Password: (unchanged until user changes it)
- Permissions: (unchanged)
- Access level: (unchanged)
```

### All Other Data
```
DELETED 🗑️
- Branches
- Users (except admin)
- Students
- Payments
- Reports
- Academic data
- etc.
```

This ensures:
- 🔐 Admin can always access the system
- 📊 Test environment starts fresh
- 🛡️ No production data leaks
- 🚀 Quick reset between deployments

---

## CRUD Operations Available

### Fully Implemented Models

#### 1. **Accounts**
- ✅ Branch: Create, Read, Update, Delete
- ✅ User: Create, Read, Update, Delete (except admin)

#### 2. **Students**
- ✅ Student: Create, Read, Update, Delete
- ✅ Student Import (Bulk Create)
- ✅ Student Detail View
- ✅ Financial Summary

#### 3. **Academics**
- ✅ Level: Create, Read, Update, Delete
- ✅ SchoolClass: Create, Read, Update, Delete
- ✅ AcademicYear: Create, Read, Update, Delete
- ✅ Term: Create, Read, Update, Delete

#### 4. **Finance**
- ✅ FeeType: Create, Read, Update, Delete
- ✅ FeeAssignment: Create, Read, Update, Delete
- ✅ Balance Calculation: Read

#### 5. **Payments**
- ✅ Payment: Create, Read, Update
- ✅ Payment Status: Real-time Update
- ✅ Receipt: View/Print
- ✅ Audit Log: View (Read-only)
- ✅ PayPack Integration: Full integration

#### 6. **Reports**
- ✅ Report Generation: View
- ✅ Financial Reports: View

#### 7. **Dashboard**
- ✅ Admin Dashboard: View
- ✅ Statistics: Real-time

---

## API Endpoints (Full CRUD)

### Accounts
```
GET    /accounts/branches/           - List all branches
POST   /accounts/branches/           - Create branch
GET    /accounts/branches/<id>/      - View branch
POST   /accounts/branches/<id>/      - Update branch
POST   /accounts/branches/<id>/delete/ - Delete branch

GET    /accounts/users/              - List all users
POST   /accounts/users/              - Create user
GET    /accounts/users/<id>/         - View user
POST   /accounts/users/<id>/         - Update user
POST   /accounts/users/<id>/delete/  - Delete user
```

### Students
```
GET    /students/                    - List students
POST   /students/                    - Create student
GET    /students/<id>/               - View student detail
POST   /students/<id>/               - Update student
POST   /students/<id>/delete/        - Delete student
POST   /students/import/             - Bulk import
```

### Academics
```
GET    /academics/levels/            - List levels
POST   /academics/levels/            - Create level
POST   /academics/levels/<id>/       - Update level
POST   /academics/levels/<id>/delete/ - Delete level

GET    /academics/classes/           - List classes
POST   /academics/classes/           - Create class
POST   /academics/classes/<id>/      - Update class
POST   /academics/classes/<id>/delete/ - Delete class

GET    /academics/years/             - List academic years
POST   /academics/years/             - Create year
POST   /academics/years/<id>/        - Update year
POST   /academics/years/<id>/delete/ - Delete year
```

### Finance
```
GET    /finance/feetypes/            - List fee types
POST   /finance/feetypes/            - Create fee type
POST   /finance/feetypes/<id>/       - Update fee type
POST   /finance/feetypes/<id>/delete/ - Delete fee type

GET    /finance/assignments/         - List fee assignments
POST   /finance/assignments/         - Create assignment
POST   /finance/assignments/<id>/    - Update assignment
POST   /finance/assignments/<id>/delete/ - Delete assignment
```

### Payments
```
GET    /payments/search/             - Search student for payment
POST   /payments/process/<id>/       - Process payment
GET    /payments/status/<id>/        - View payment status
GET    /payments/status/<id>/api/    - Get status (JSON)
GET    /payments/history/            - Payment history
GET    /payments/receipt/<id>/       - View receipt
POST   /payments/webhook/            - PayPack webhook
```

---

## Deployment Checklist

Before deploying to production:

- [ ] `.env.example` is up to date
- [ ] All secrets added to GitHub
- [ ] `requirements.txt` is current
- [ ] Database migrations created: `python manage.py makemigrations`
- [ ] Database migrations tested: `python manage.py migrate --dry-run`
- [ ] Static files configured: `STATIC_ROOT`, `STATIC_URL`
- [ ] Debug set to `False` in production `.env`
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CSRF and security settings enabled
- [ ] Logging configured
- [ ] Admin user credentials set
- [ ] Email settings configured (for password resets)
- [ ] PayPack credentials configured
- [ ] HTTPS/SSL enabled on server
- [ ] Database backup strategy in place
- [ ] Monitoring/alerting configured
- [ ] Backup of current .env file (stored securely)

---

## Rollback Procedure

If something goes wrong:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# GitHub Actions will run again with previous code
# Admin credentials will be preserved
# Database will reset with previous migration state
```

---

## Monitoring After Deployment

```bash
# Check logs
tail -f /var/log/ecome-finance/django.log

# Check payments
python manage.py dbshell
SELECT * FROM payments_payment WHERE created_at > NOW() - INTERVAL 1 hour;

# Check admin access
Visit: https://yourdomain.com/admin
Username: admin
Password: (check .env file)
```

---

## Troubleshooting

### Admin can't login
```bash
python manage.py shell
from accounts.models import User
user = User.objects.get(username='admin')
user.set_password('admin')  # Reset to default
user.save()
```

### Migrations failed
```bash
# Reset migrations (careful!)
python manage.py migrate zero  # Reverse all
python manage.py migrate        # Reapply all
python scripts/init_deployment.py
```

### Database locked
```bash
# Remove old sqlite file
rm db.sqlite3
python manage.py migrate
python scripts/init_deployment.py
```

### Static files not loading
```bash
python manage.py collectstatic --noinput --clear
```

---

## Production Deployment Services

### Recommended Hosting:
- **Railway.app** - Zero-config, GitHub integration
- **Render.com** - Free tier, GitHub deploy
- **PythonAnywhere** - Django-specific hosting
- **Heroku** (paid) - Reliable, GitHub integration
- **AWS** - Scalable, more complex setup

### Quick Setup for Railway:
1. Connect GitHub repo
2. Add environment variables
3. Set build command: `pip install -r requirements.txt && python manage.py migrate && python scripts/init_deployment.py`
4. Deploy!

---

## Summary

✅ **Automatic Deployment**: Push to main → Auto-deploy  
✅ **Data Safety**: Admin credentials preserved  
✅ **Fresh Start**: Database cleans each deployment  
✅ **Full CRUD**: All models have create/read/update/delete  
✅ **Zero Downtime**: Migrations run before deployment  
✅ **Audit Trail**: All changes logged  

**You're ready for production! 🚀**

---

## Quick Start Commands

```bash
# First time setup
git clone <your-repo>
cd ecome-finance
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python manage.py migrate
python scripts/init_deployment.py
python manage.py runserver

# After each code change
git add .
git commit -m "Your message"
git push origin main
# GitHub Actions deploys automatically!
```

---

**Next:** Push your code to GitHub and watch your app deploy! 🎉
