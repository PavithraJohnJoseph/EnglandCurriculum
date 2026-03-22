import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check for superusers
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print('✅ EXISTING SUPERUSER(S) FOUND:')
    print('=' * 40)
    for user in superusers:
        print(f'Username: {user.username}')
        print(f'Email: {user.email}')
        print(f'Last login: {user.last_login or "Never"}')
        print('')
    print('🔗 Access admin at: http://127.0.0.1:8000/admin/')
else:
    print('❌ NO SUPERUSER FOUND')
    print('=' * 40)
    print('You need to create a superuser first.')
    print('')
    print('Run this command to create one:')
    print('python manage.py createsuperuser')
    print('')
    print('Or I can create one for you automatically...')