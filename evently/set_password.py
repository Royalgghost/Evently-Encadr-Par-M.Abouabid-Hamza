import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evently.settings')
django.setup()

from django.contrib.auth.models import User

# Get the admin user and set password
user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()

print("Password for admin user has been set to 'admin123'")
