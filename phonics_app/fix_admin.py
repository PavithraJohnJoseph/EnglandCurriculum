import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print('🔍 CHECKING ADMIN USER STATUS')
print('=' * 40)

# Check if admin user exists
try:
    admin_user = User.objects.get(username='admin')
    print(f'✅ Admin user found: {admin_user.username}')
    print(f'   Email: {admin_user.email}')
    print(f'   Is superuser: {admin_user.is_superuser}')
    print(f'   Is staff: {admin_user.is_staff}')
    print(f'   Is active: {admin_user.is_active}')

    # Check password
    if admin_user.check_password('admin123'):
        print('   ✅ Password is correct')
    else:
        print('   ❌ Password is incorrect - resetting...')
        admin_user.set_password('admin123')
        admin_user.save()
        print('   ✅ Password reset to: admin123')

    # Ensure superuser permissions
    if not admin_user.is_superuser or not admin_user.is_staff:
        print('   ⚠️ Missing permissions - fixing...')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print('   ✅ Superuser permissions granted')

except User.DoesNotExist:
    print('❌ Admin user does not exist - creating now...')
    User.objects.create_superuser(
        username='admin',
        email='admin@phonicsapp.com',
        password='admin123'
    )
    print('✅ Admin user created successfully!')

print('')
print('🔑 LOGIN CREDENTIALS:')
print('   Username: admin')
print('   Password: admin123')
print('   URL: http://127.0.0.1:8000/admin/')
print('')
print('🎯 Try logging in again!')