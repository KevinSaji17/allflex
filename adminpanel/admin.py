from django.contrib import admin
from django.conf import settings

# Customize admin site headers
admin.site.site_header = "ALLFLEX Administration"
admin.site.site_title = "ALLFLEX Admin Portal"
admin.site.index_title = "Welcome to ALLFLEX Administration"

# MongoDB user management note
if settings.DATABASE_MODE == 'mongodb':
    # MongoDB users are managed through the UserProfile model
    # They can be managed via Django shell commands or custom management commands
    # Example: python manage.py shell
    # >>> from accounts.mongo_models import UserProfile
    # >>> user = UserProfile.objects(username='example').first()
    # >>> user.role = 'gym_owner'
    # >>> user.save()
    pass
