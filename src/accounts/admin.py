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
                "fields": ("email", "username", "password1", "password2", "first_name", "last_name"),
            },
        ),
    )

    list_display = ("email", "username", "first_name", "last_name", "is_staff")


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at']
