from django.contrib.auth.models import User
from django.core.management import setup_environ
import sys
import os

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import settings
from evently import settings
setup_environ(settings)

# Set admin password
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.save()

print("Admin password set to 'admin123'")
