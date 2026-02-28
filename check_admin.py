import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin = User.objects.using('default').get(username='admin')
    print('✅ Admin user found in SQL database')
    print(f'Username: {admin.username}')
    print(f'Email: {admin.email}')
    print(f'Is Staff: {admin.is_staff}')
    print(f'Is Superuser: {admin.is_superuser}')
    print(f'Has usable password: {admin.has_usable_password()}')
    print('')
    print('🔑 Admin Panel Access:')
    print('URL: http://localhost:8000/admin/')
    print('Username: admin')
    print('Password: admin123')
except User.DoesNotExist:
    print('❌ Admin user not found - creating now...')
    admin = User(
        username='admin',
        email='admin@allflex.com',
        is_staff=True,
        is_superuser=True,
        role='admin'
    )
    admin.set_password('admin123')
    admin.save(using='default')
    print('✅ Admin user created successfully!')
    print('Username: admin')
    print('Password: admin123')
except Exception as e:
    print(f'❌ Error: {e}')
