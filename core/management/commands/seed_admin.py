from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role

class Command(BaseCommand):
    help = "Seeds default roles and creates the super admin account"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # 1️⃣ Create roles
        roles_data = [
            {"name": "admin", "display_name": "Admin"},
            {"name": "vendor", "display_name": "Vendor"},
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(**role_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Role '{role.display_name}' created"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Role '{role.display_name}' already exists"))

        # 2️⃣ Create super admin
        if not User.objects.filter(username="Admin").exists():
            admin_role = Role.objects.get(name="admin")
            User.objects.create_superuser(
                username="Admin",
                email="admin@gmail.com",
                password="Admin@2025",
                role=admin_role
            )
            self.stdout.write(self.style.SUCCESS("✅ Super admin 'Admin' created"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Super admin 'Admin' already exists"))
