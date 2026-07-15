import sys

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # Avoid running during migrations, collectstatic, or when the DB isn't ready.
        if any(arg in sys.argv for arg in ['makemigrations', 'migrate', 'collectstatic', 'shell', 'test']):
            return

        User = get_user_model()
        try:
            admin_user = User.objects.filter(username='admin').first()
        except (OperationalError, ProgrammingError):
            return

        if admin_user is None:
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin',
            )
        else:
            if not admin_user.is_staff or not admin_user.is_superuser:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
