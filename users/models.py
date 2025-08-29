from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils import profile_image_upload


class Role(models.Model):
    """
    Stores different user roles dynamically.
    """
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.display_name


class User(AbstractUser):
    """
    Custom User model with dynamic role assignment.
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    profile_picture = models.ImageField(
        upload_to=profile_image_upload,
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.username} ({self.role.display_name if self.role else 'No role'})"

    def is_role(self, role_name):
        """Check if the user has a given role name (case-insensitive)."""
        return self.role and self.role.name.lower() == role_name.lower()
    
    @property
    def is_admin(self):
        return self.is_role("admin")

    @property
    def is_vendor(self):
        return self.is_role("vendor")

