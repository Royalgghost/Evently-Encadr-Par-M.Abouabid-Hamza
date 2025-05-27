import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evently.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile

# Admin credentials
username = 'admin'
new_password = 'admin123'  # You can change this to any password you prefer
email = 'admin@example.com'

# Try to get admin user or create if doesn't exist
try:
    admin_user = User.objects.get(username=username)
    admin_user.set_password(new_password)
    admin_user.save()
    print(f"Admin password has been reset to: {new_password}")
except User.DoesNotExist:
    # Create new admin user
    admin_user = User.objects.create_superuser(
        username=username,
        email=email,
        password=new_password,
        first_name='Admin',
        last_name='User'
    )
    print(f"Admin user created with password: {new_password}")

# Ensure admin has a UserProfile with admin role
try:
    profile = UserProfile.objects.get(user=admin_user)
    profile.role = 'admin'
    profile.save()
    print("Admin profile updated.")
except UserProfile.DoesNotExist:
    # Create admin profile
    UserProfile.objects.create(
        user=admin_user,
        role='admin',
        bio='System Administrator'
    )
    print("Admin profile created.")

print("\nYou can now log in with:")
print(f"Username: {username}")
print(f"Password: {new_password}")
print("\nUse this account to access the admin dashboard at /dashboard/")
print("Or the Django admin interface at /admin/")
