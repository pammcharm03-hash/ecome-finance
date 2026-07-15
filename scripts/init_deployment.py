"""
Deployment initialization script.
Resets database but preserves admin user credentials.
Runs automatically on deployment.

Usage:
    python manage.py shell < scripts/init_deployment.py
    OR
    python scripts/init_deployment.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecome_finance.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from accounts.models import User as CustomUser
import logging

logger = logging.getLogger('deployment')

def preserve_admin():
    """Store admin credentials before reset."""
    try:
        admin = CustomUser.objects.filter(username='admin', is_admin=True).first()
        if admin:
            admin_data = {
                'username': admin.username,
                'email': admin.email,
                'password_hash': admin.password,
                'is_admin': True,
                'is_active': True,
            }
            return admin_data
    except:
        pass
    return None

def restore_admin(admin_data):
    """Restore admin after reset."""
    if not admin_data:
        return
    
    try:
        admin, created = CustomUser.objects.get_or_create(
            username=admin_data['username'],
            defaults={
                'email': admin_data['email'],
                'is_admin': True,
                'is_active': True,
            }
        )
        # Restore password hash
        admin.password = admin_data['password_hash']
        admin.save()
        print(f"✓ Admin user restored: {admin.username}")
    except Exception as e:
        print(f"✗ Error restoring admin: {e}")

def run_deployment():
    """Run deployment initialization."""
    print("\n" + "="*50)
    print("🚀 DEPLOYMENT INITIALIZATION")
    print("="*50 + "\n")
    
    # Step 1: Preserve admin
    print("📝 Preserving admin credentials...")
    admin_data = preserve_admin()
    if admin_data:
        print(f"✓ Admin credentials saved: {admin_data['username']}")
    else:
        print("⚠ No admin user found to preserve")
    
    # Step 2: Clean database
    print("\n🧹 Cleaning database...")
    try:
        # Remove database file
        db_file = 'db.sqlite3'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"✓ Removed {db_file}")
    except Exception as e:
        print(f"✗ Error removing database: {e}")
    
    # Step 3: Run migrations
    print("\n🔄 Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed")
    except Exception as e:
        print(f"✗ Migration error: {e}")
    
    # Step 4: Restore admin
    print("\n🔐 Restoring admin credentials...")
    restore_admin(admin_data)
    
    # Step 5: Create initial data (optional)
    print("\n📊 Creating initial setup...")
    try:
        from django.utils import timezone
        from accounts.models import Branch
        
        # Create default branch if not exists
        branch, created = Branch.objects.get_or_create(
            name='Main Campus',
            defaults={'code': 'MAIN', 'is_active': True}
        )
        if created:
            print(f"✓ Created default branch: {branch.name}")
        else:
            print(f"✓ Default branch exists: {branch.name}")
            
    except Exception as e:
        print(f"⚠ Note: {e}")
    
    print("\n" + "="*50)
    print("✅ DEPLOYMENT INITIALIZATION COMPLETE!")
    print("="*50 + "\n")

if __name__ == '__main__':
    run_deployment()
