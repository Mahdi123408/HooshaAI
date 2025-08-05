import datetime
import uuid
import jwt
from django.utils import timezone
from authentication.models import AccessToken, RefreshToken
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError

def create_access_token(user):
    token_id = str(uuid.uuid4())
    now = timezone.now()
    exp = now + settings.ACCESS_TOKEN_LIFETIME

    payload = {
        "jti": token_id,
        "type": "at",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "sub": str(user.id)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    AccessToken.objects.create(
        token=token,
        user=user,
        token_id=token_id,
        created_at=now,
        expires_at=exp
    )

    return token



def create_refresh_token(user):
    token_id = str(uuid.uuid4())
    now = timezone.now()
    exp = now + settings.REFRESH_TOKEN_LIFETIME

    payload = {
        "jti": token_id,
        "type": "rt",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "sub": str(user.id)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    RefreshToken.objects.create(
        token=token,
        user=user,
        token_id=token_id,
        created_at=now,
        expires_at=exp
    )

    return token


def decode_and_validate_token(token: str, expected_type: str):
    try:
        parts = token.split(' ')
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None, "invalid_format"

        token = parts[1]
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

    except ExpiredSignatureError:
        return None, "expired"
    except InvalidTokenError:
        return None, "invalid"

    if payload.get("type") != expected_type:
        return None, "wrong_type"

    token_id = payload.get("jti")
    if expected_type == "at":
        token_obj = AccessToken.objects.filter(token=token, token_id=token_id).first()
    else:
        token_obj = RefreshToken.objects.filter(token=token, token_id=token_id).first()

    if not token_obj or not token_obj.user.is_active:
        return None, "not_found"

    return token_obj.user, "valid"
