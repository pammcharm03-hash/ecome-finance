from accounts.models import User
if not User.objects.filter(username='devadmin').exists():
    User.objects.create_superuser('devadmin','devadmin@example.com','DevPass123!')
    print('Created devadmin')
else:
    print('devadmin exists')
