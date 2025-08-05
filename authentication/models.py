from django.db import models
from user.models import CustomUser
from django.utils import timezone


class AccessToken(models.Model):
    token = models.CharField(max_length=512, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    token_type = models.CharField(max_length=2, default='at', editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='access_tokens', db_index=True)
    token_id = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return f'{self.user.username} - Access Token (expires {self.expires_at})'

    def is_expired(self):
        return timezone.now() >= self.expires_at

    class Meta:
        verbose_name = 'Access Token'
        verbose_name_plural = 'Access Tokens'


class RefreshToken(models.Model):
    token = models.CharField(max_length=512, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    token_type = models.CharField(max_length=2, default='rt', editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='refresh_tokens', db_index=True)
    token_id = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return f'{self.user.username} - Refresh Token (expires {self.expires_at})'

    def is_expired(self):
        return timezone.now() >= self.expires_at

    class Meta:
        verbose_name = 'Refresh Token'
        verbose_name_plural = 'Refresh Tokens'
