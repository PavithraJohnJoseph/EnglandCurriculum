import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print('👑 LIST OF ALL SUPERUSERS IN DATABASE')
print('=' * 50)

superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    print(f'✅ Found {superusers.count()} superuser(s):')
    print('')

    for i, user in enumerate(superusers, 1):
        print(f'{i}. Username: {user.username}')
        print(f'   Email: {user.email}')
        print(f'   Full Name: {user.get_full_name() or "Not set"}')
        print(f'   Is Active: {user.is_active}')
        print(f'   Is Staff: {user.is_staff}')
        print(f'   Last Login: {user.last_login or "Never"}')
        print(f'   Date Joined: {user.date_joined}')
        print('')

else:
    print('❌ No superusers found in database')
    print('')
    print('💡 To create a superuser, run:')
    print('   python manage.py createsuperuser')

print('')
print('📊 TOTAL USERS IN DATABASE:')
all_users = User.objects.all()
print(f'   Total users: {all_users.count()}')

if all_users.count() > 0:
    print('')
    print('📋 ALL USERS (including regular users):')
    for user in all_users:
        status = []
        if user.is_superuser:
            status.append('SUPERUSER')
        if user.is_staff:
            status.append('STAFF')
        status_str = f" ({', '.join(status)})" if status else ""

        print(f'   - {user.username} ({user.email}){status_str}')