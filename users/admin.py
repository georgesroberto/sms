

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name")
    search_fields = ("name", "display_name")


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ( "profile_pic_preview", "username", "email", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "role__display_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {
            "fields": ("username", "email", "password")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "profile_picture", "bio", "role")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role"),
        }),
    )

    def profile_pic_preview(self, obj):
        """Show small profile picture preview in admin list."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "—"
    profile_pic_preview.short_description = "Profile Pic"
