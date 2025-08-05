from rest_framework import serializers
from user.models import CustomUser
from utils.validators import validate_phone
from setting.models import Role
import re
class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'phone', 'role', 'cover_url', 'avatar_url', 'created_at', 'updated_at']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'full_name', 'phone']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError({
                'fa':[
                    'نام کاربری فقط می‌تواند شامل حروف، اعداد و خط زیر ( _ ) باشد.'
                ],
                'en':[
                    'Username can only contain letters, numbers, and underscores.'
                ]
            })
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError({
                'fa':[
                    'نام کاربری قبلاً استفاده شده است.'
                ],
                'en':[
                    'Username is already taken.'
                ]
            })
        return value

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a valid email address.")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@!_.#]', value):
            raise serializers.ValidationError("Password must contain at least one special character (@, !, _ , # or .).")
        return value

    def validate_phone(self, value):
        value = validate_phone(value)
        if not re.match(r'^(09|9)\d{9}$', value):
            raise serializers.ValidationError("Phone number must start with 09 or 9 and be 10 or 11 digits long.")
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        role = Role.objects.get(dev_name='b')
        validated_data['role'] = role
        user = CustomUser.objects.create(**validated_data)
        user.set_password(user.password)
        return user