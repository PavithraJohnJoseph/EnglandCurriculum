import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print('🔧 FIXING ADMIN LOGIN ISSUE')
print('=' * 40)

# Delete existing admin if it exists
User.objects.filter(username='admin').delete()
print('✅ Deleted any existing admin user')

# Create fresh superuser
User.objects.create_superuser('admin', 'admin@phonicsapp.com', 'admin123')
print('✅ Created fresh admin superuser')

print('')
print('🔑 ADMIN LOGIN CREDENTIALS:')
print('   Username: admin')
print('   Password: admin123')
print('   Email: admin@phonicsapp.com')
print('')
print('🌐 Access admin at: http://127.0.0.1:8000/admin/')
print('')
print('🎯 Try logging in now!')