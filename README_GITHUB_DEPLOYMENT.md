# 🎓 ECOME Finance - School Finance Management System

A comprehensive Django-based school finance management system with integrated mobile money payments (PayPack), student fee tracking, and financial reporting.

## ✨ Features

### 📚 Student Management
- Student registration and profile management
- Bulk student import from Excel/CSV
- Student classification by class, level, branch
- Parent contact information tracking

### 💰 Finance Management
- Fee type configuration
- Fee assignment by scope (school, branch, level, class)
- Student balance calculation
- Fee payment tracking

### 📱 Payment Integration
- **PayPack Mobile Money Integration**
- Real-time payment status checking
- Automatic payment confirmation via webhook
- Payment receipt generation
- Payment history and auditing
- Multiple payment methods support

### 📊 Reports & Analytics
- Financial dashboards
- Revenue tracking
- Payment status reports
- Student balance reports
- Branch-wise reporting

### 🔐 Security & Access Control
- Role-based access control (Admin, Registrar, Accountant)
- Branch isolation for multi-branch systems
- Audit logging of all transactions
- User authentication and authorization

### 📈 Admin Dashboard
- Real-time statistics
- Revenue charts
- Payment status overview
- Quick action buttons
- Recent transactions list

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (venv)
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecome-finance.git
cd ecome-finance
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize database**
```bash
python manage.py migrate
python scripts/init_deployment.py
```

6. **Create superuser (optional - admin/admin already exists)**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

---

## 📖 Usage

### Default Credentials
```
Username: admin
Password: admin
```

### Main Features

#### 1. Student Management
- Dashboard → Students → Manage Students
- Add individual students or bulk import
- Track student balance and fees

#### 2. Fee Configuration
- Dashboard → Finance → Fee Types
- Create fee categories (Tuition, Books, Uniforms, etc.)
- Assign fees to students by scope

#### 3. Payment Processing
- Dashboard → Payments → Search Student
- Select fee type and amount
- Enter parent's mobile number
- Parent receives Mobile Money prompt
- Payment confirmation automatic or manual

#### 4. Reports
- Dashboard → Reports → View Reports
- Generate financial summaries
- Export data for accounting

---

## 🔄 Automatic Deployment

### GitHub Integration

Every time you push to the `main` branch, the system automatically:

1. **Runs Tests**
   - Django configuration checks
   - Migration validation
   - Dependency verification

2. **Resets Database**
   - Removes old data
   - Creates fresh database
   - **Preserves admin/admin credentials**
   - Creates default branch

3. **Deploys Code**
   - Collects static files
   - Runs migrations
   - Deploys to production

4. **Verifies Deployment**
   - Checks security settings
   - Verifies admin access
   - Confirms application health

### Setup GitHub Deployment

1. **Add Repository Secrets**
   ```
   Settings → Secrets and variables → Actions
   ```

   Required secrets:
   - `SECRET_KEY` - Django secret key
   - `ALLOWED_HOSTS` - Allowed domain names
   - `DATABASE_URL` - Database connection string
   - `PAYPACK_CLIENT_ID` - PayPack credentials
   - `PAYPACK_CLIENT_SECRET` - PayPack secret
   - `PAYPACK_WEBHOOK_URL` - Webhook URL

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your message"
   git push origin main
   ```

3. **Monitor Deployment**
   - Go to GitHub → Actions
   - Watch the deployment workflow
   - Check logs for any issues

---

## 🛠️ CRUD Operations

All major entities have full Create, Read, Update, Delete operations:

### Student Management
- ✅ Create students
- ✅ View student details and balance
- ✅ Update student information
- ✅ Delete student records
- ✅ Bulk import students

### Fee Management
- ✅ Create fee types
- ✅ View fee assignments
- ✅ Update fee amounts
- ✅ Delete fee types

### Accounts
- ✅ Create branches
- ✅ View branch details
- ✅ Update branch information
- ✅ Delete branches
- ✅ Create user accounts
- ✅ Manage user roles and permissions

### Academics
- ✅ Create levels (Form 1, Form 2, etc.)
- ✅ Create classes
- ✅ Create academic years
- ✅ Update all academic information
- ✅ Delete academic records

### Payments
- ✅ Create payment records
- ✅ View payment history
- ✅ Update payment status
- ✅ View receipts
- ✅ Audit payment logs

---

## 📝 Database Structure

### Core Models
- **User** - System users with role-based access
- **Branch** - School branches for multi-campus support
- **Student** - Student information and enrollment
- **Level** - Academic levels (Form 1-6)
- **SchoolClass** - Class information
- **AcademicYear** - School year definition

### Finance Models
- **FeeType** - Fee categories (Tuition, Books, etc.)
- **FeeAssignment** - Fee amounts for different scopes
- **Payment** - Payment records with status tracking

### Integration Models
- **AuditLog** - Complete audit trail of all actions

---

## 🔌 PayPack Integration

### How It Works

1. **Payment Initiation**
   - Accountant searches for student
   - Selects fee type and amount
   - Enters parent's phone number

2. **PayPack Request**
   - System sends payment request to PayPack
   - Includes phone number and amount
   - Returns transaction reference

3. **Parent Confirmation**
   - Parent receives Mobile Money prompt
   - Enters PIN to confirm payment
   - PayPack processes the payment

4. **Confirmation**
   - Two methods:
     - Webhook callback (automatic)
     - Manual status check (manual polling)

5. **Receipt**
   - Payment marked as successful
   - Receipt can be printed
   - Audit log recorded

### Configuration

Set in `.env`:
```
PAYPACK_CLIENT_ID=your-client-id
PAYPACK_CLIENT_SECRET=your-client-secret
PAYPACK_WEBHOOK_URL=https://yourdomain.com/payments/webhook/
```

---

## 📊 Admin Dashboard

The admin dashboard provides:

- **Today's Revenue** - Revenue collected today
- **Weekly Revenue** - Revenue this week
- **Monthly Revenue** - Revenue this month
- **Total Students** - Total enrolled students
- **Statistics**
  - Total branches
  - Total users
  - Total fee types
  - Total payments
- **Charts**
  - Revenue by fee type
  - Revenue by branch
  - Revenue by class (top 10)
- **Recent Transactions** - Latest 10 payments
- **Quick Actions** - Fast links to common tasks

---

## 🔒 Security Features

- ✅ HTTPS support
- ✅ CSRF protection
- ✅ XFrame options set to DENY
- ✅ HTTP headers for security
- ✅ Cookie security (HttpOnly, Secure flags)
- ✅ HSTS headers (in production)
- ✅ Role-based access control
- ✅ Branch isolation
- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ Audit logging of all actions

---

## 📋 Project Structure

```
ecome-finance/
├── accounts/              # User management
├── academics/             # Academic structure (levels, classes, years)
├── students/              # Student management
├── finance/               # Fee configuration
├── payments/              # Payment processing & PayPack integration
├── reports/               # Financial reports
├── dashboard/             # Admin dashboard
├── core/                  # Core utilities and context processors
├── ecome_finance/         # Django settings
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── scripts/               # Deployment and utility scripts
├── .github/workflows/     # GitHub Actions workflows
└── manage.py              # Django management script
```

---

## 🧪 Testing

### Run CRUD Tests
```bash
python manage.py shell < scripts/test_crud.py
```

### Run Django Checks
```bash
python manage.py check
```

### Run Migrations Dry Run
```bash
python manage.py migrate --dry-run
```

---

## 📚 Documentation

- [**Auto Deployment Guide**](GITHUB_AUTO_DEPLOYMENT.md) - GitHub Actions setup
- [**PayPack Integration**](PAYPACK_INTEGRATION_FIXES.md) - Payment system details
- [**Deployment Checklist**](DEPLOYMENT_CHECKLIST.md) - Production deployment steps

---

## 🚢 Deployment

### Quick Deployment

**On Linux/Mac:**
```bash
bash scripts/deploy.sh
```

**On Windows (PowerShell):**
```powershell
.\scripts\deploy.ps1
```

### Prepare for GitHub Push
```bash
bash scripts/prepare_push.sh
```

---

## 🔗 API Endpoints

### Authentication
```
POST   /accounts/login/              - User login
GET    /accounts/logout/             - User logout
```

### Student Management
```
GET    /students/                    - List students
POST   /students/                    - Create student
GET    /students/<id>/               - View student
POST   /students/<id>/               - Update student
POST   /students/<id>/delete/        - Delete student
```

### Payment Processing
```
GET    /payments/search/             - Find student
POST   /payments/process/<id>/       - Process payment
GET    /payments/status/<id>/        - Payment status
GET    /payments/status/<id>/api/    - Status API (JSON)
GET    /payments/receipt/<id>/       - View receipt
GET    /payments/history/            - Payment history
```

### Full API list in [GITHUB_AUTO_DEPLOYMENT.md](GITHUB_AUTO_DEPLOYMENT.md)

---

## 🐛 Troubleshooting

### Admin Login Issues
```bash
python manage.py shell
from accounts.models import User
user = User.objects.get(username='admin')
user.set_password('admin')
user.save()
```

### Database Reset
```bash
rm db.sqlite3
python manage.py migrate
python scripts/init_deployment.py
```

### Migration Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review GitHub Issues
3. Check deployment logs: `tail -f /var/log/ecome-finance/django.log`

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Contributors

- Development Team
- ECOME Finance

---

## 🎯 Roadmap

- [ ] SMS notifications for payment status
- [ ] Mobile app for parents
- [ ] Advanced financial reporting
- [ ] Payment installment plans
- [ ] Multi-currency support
- [ ] Integration with accounting software
- [ ] Student portal

---

## ✅ Ready to Deploy?

1. ✅ All CRUD operations implemented
2. ✅ Admin credentials preserved on deployment
3. ✅ Database auto-reset on each deployment
4. ✅ GitHub Actions auto-deployment configured
5. ✅ PayPack integration complete
6. ✅ Security hardened
7. ✅ Documentation complete

**Start deploying now!** 🚀

```bash
git push origin main
```

Watch your app auto-deploy in GitHub Actions! 🎉

---

**Last Updated:** 2026-07-15  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
