from django.contrib import admin
from user.models import *


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'encripted_password', 'full_name', 'role', 'is_active']

    def encripted_password(self, obj):
        return obj.password[:5] + ' ... .'
