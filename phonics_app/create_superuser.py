import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user exists
if User.objects.filter(username='admin').exists():
    print('✅ Superuser "admin" already exists!')
else:
    # Create superuser
    User.objects.create_superuser(
        username='admin',
        email='admin@phonicsapp.com',
        password='admin123'
    )
    print('✅ Superuser "admin" created successfully!')

print('')
print('🔑 ADMIN LOGIN CREDENTIALS:')
print('   Username: admin')
print('   Password: admin123')
print('   Email: admin@phonicsapp.com')
print('')
print('🌐 Access admin panel at:')
print('   http://127.0.0.1:8000/admin/')
print('')
print('💡 You can change the password later in the admin panel!')