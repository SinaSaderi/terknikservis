"""Integrate with admin module."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no mobile field."""

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'company', 'telephone', 'address', 'email', 'website')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2'),
        }),
    )
    list_display = ('mobile', 'first_name', 'last_name', 'is_staff')
    search_fields = ('mobile', 'first_name', 'last_name')
    ordering = ('mobile',)