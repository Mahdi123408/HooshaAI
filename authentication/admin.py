from django.contrib import admin
from authentication.models import *

@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'at_token', 'created_at', 'expires_at', 'token_type', 'user', 'token_id']

    def at_token(self, obj):
        return obj.token[:8] + ' ... .'


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'rt_token', 'created_at', 'expires_at', 'token_type', 'user', 'token_id']

    def rt_token(self, obj):
        return obj.token[:8] + ' ... .'