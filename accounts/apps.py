import sys

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError
from django.db.models.signals import post_migrate


def create_default_admin(sender, **kwargs):
    if sys.argv[1:2] == ['test']:
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
        admin_user = User.objects.get(username='admin')
    if admin_user.role != User.Role.ADMIN:
        admin_user.role = User.Role.ADMIN
    if not admin_user.is_staff or not admin_user.is_superuser:
        admin_user.is_staff = True
        admin_user.is_superuser = True
    admin_user.save()


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)
