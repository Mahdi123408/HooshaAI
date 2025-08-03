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
