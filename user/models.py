from django.utils import timezone

from django.db import models

from setting.models import Role
from django.contrib.auth.hashers import make_password, check_password


class CustomUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    cover_url = models.ImageField(upload_to='covers', null=True, blank=True)
    avatar_url = models.ImageField(upload_to='avatars', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users', verbose_name='user role')
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    can_message_me = models.BooleanField(default=True)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username} - {self.full_name}'

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def active_sessions_count(self):
        from authentication.models import RefreshToken
        now = timezone.now()
        return RefreshToken.objects.filter(user=self, expires_at__gt=now).count()

    def update_last_seen(self):
        self.last_seen = timezone.now()
        self.save()

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
        }
        return data


class BlockUser(models.Model):
    user = models.ForeignKey(CustomUser, related_name='blocked_users', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(CustomUser, related_name='blocked_of_users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.blocked_user.username} of {self.user.username}'
