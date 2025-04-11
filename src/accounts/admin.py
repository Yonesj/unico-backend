from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivationCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin panel for the User model.
    """

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "full_name"),
            },
        ),
    )

    list_display = ("email", "username", "full_name", "is_ui_student", "is_staff")
    list_filter = ("is_ui_student", "is_staff", "is_superuser", "is_active", "groups")

    fieldsets = (
        (None, {"fields": ("email", "username", "password", "full_name")}),
        ("Permissions", {"fields": ("is_active", "is_ui_student", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at']
