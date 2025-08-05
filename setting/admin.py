from django.contrib import admin
from setting.models import *

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'dev_name', 'count_access_token']