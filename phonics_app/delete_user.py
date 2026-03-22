import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonics_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if JP user exists
exists = User.objects.filter(username='JP').exists()
if exists:
    print('❌ User JP still exists')
    # Delete the user
    user = User.objects.get(username='JP')
    user.delete()
    print('✅ User JP has been deleted successfully!')
else:
    print('✅ User JP was already deleted or never existed!')

# Show remaining users
print('\n📊 Remaining users in database:')
all_users = User.objects.all()
if all_users:
    for user in all_users:
        print(f'   - {user.username} ({user.email}) - Verified: {user.email_verified}')
else:
    print('   No users found in database.')