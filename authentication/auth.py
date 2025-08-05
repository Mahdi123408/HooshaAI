from rest_framework.request import Request
from authentication.jwt import decode_and_validate_token
from user.models import CustomUser
from django.db.models import Q
from HooshaAI.settings import CUSTOM_ACCESS_TOKEN_NAME

def get_authenticated_user_from_request(request: Request):
    auth_header = request.headers.get(CUSTOM_ACCESS_TOKEN_NAME)
    if not auth_header:
        return None

    user, status = decode_and_validate_token(auth_header, expected_type='at')
    if status == 'valid':
        return user
    else:
        return None


def authenticate_user(data):
    identifier = data.get('username') or data.get('email')
    password = data.get('password')

    if not identifier or not password:
        return None

    try:
        user = CustomUser.objects.get(Q(username=identifier) | Q(email=identifier))
    except CustomUser.DoesNotExist:
        return None

    if user.check_password(password) and user.is_active:
        return user

    return None
