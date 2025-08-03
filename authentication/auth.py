from rest_framework.request import Request
from authentication.jwt import decode_and_validate_token

def get_authenticated_user_from_request(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    user, status = decode_and_validate_token(auth_header, expected_type='at')
    if status == 'valid':
        return user
    else:
        return None
