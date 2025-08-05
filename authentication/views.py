from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpRequest
from authentication import auth
from HooshaAI.settings import CUSTOM_ACCESS_TOKEN_NAME
from rest_framework.response import Response
from authentication.serializers import UserViewSerializer, CustomUserCreateSerializer
from rest_framework import status
from authentication import jwt


class UserAPIView(APIView):

    @swagger_auto_schema(
        operation_description="برگرداندن اطلاعات کاربر .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
            200:
                openapi.Response(
                    description="اطلاعات یوزر . ",
                    examples={
                        "application/json": {
                            "user": {
                                "username": "mahdi_abbasi_from_api",
                                "email": "abasimahdi253@gmail.com",
                                "full_name": "مهدی عباسی",
                                "phone": "09055601501",
                                "role": "normal",
                                "ivt_balance": 0,
                                "wallet_address": "ohvajoi",
                                "rating": 0,
                                "level": 0,
                                "cover_url": None,
                                "avatar_url": None,
                                "telegram_id": None,
                                "instagram_id": None,
                                "points": 0,
                                "created_at": "2024-06-12T03:39:25.591550+03:30",
                                "updated_at": "2024-06-12T04:04:27.128266+03:30"
                            }
                        }
                    }

                )
        },
    )
    def get(self, request: HttpRequest):
        user = auth.get_authenticated_user_from_request(request)
        if user:
            try:
                serializer = UserViewSerializer(user)
                return Response(data={'user': serializer.data}, status=status.HTTP_200_OK)
            except Exception:
                data = {
                    'errors': {
                        'fa': [
                            'خطای در پردازش اطلاعات کاربر رخ داد!',
                        ],
                        'en': [
                            'An error occurred while processing user data!',
                        ]
                    }
                }
                return Response(data=data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            data = {
                'errors': {
                    'fa': [
                        'نشست شما اعتبار ندارد مجددا وارد شوید!',
                    ],
                    'en': [
                        'Your session is invalid. Please log in again!',
                    ]
                }
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)



class LoginAPIView(APIView):

    @swagger_auto_schema(
        operation_description="دادن نام کاربری و رمز و دریافت اکسس توکن و رفرش توکن .",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           default='mahdi_abbasi_from_api'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='رمز عبور', default='@Aa123456'),
            },
            required=['username', 'password']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در ورود کاربر",
                examples={
                    "application/json": "Login Failed"
                }
            ),
            200: openapi.Response(
                description="اکسس توکن و رفرش توکن . ",
                examples={
                    "application/json": {

                        'access': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkIjoiMjAyNC0wNi0xNCAxODowNDo1OSIsInRva2VuX2lkIjoiMjA1OWMwYzgtOWZhYy00M2JjLTlkYTMtODM2NTc0MmM3N2QxIiwiZXhwdCI6IjIwMjQtMDYtMTUgMTg6MDQ6NTkiLCJ0eXBlIjoiYXQifQ.CSaB2QABFXi4B-SALqHsUXuZpn2EydvGvTpdeMfMwr8",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkIjoiMjAyNC0wNi0xNCAxODowNDo1OSIsInRva2VuX2lkIjoiNzZkYjI2ZTItNjdhYS00ZmYwLTlhOGQtYWQ2YzllOGQ2MjBmIiwiZXhwdCI6IjIwMjQtMDYtMTcgMTg6MDQ6NTkiLCJ0eXBlIjoicnQifQ.3g9sPymcpemDrMrRLfXKV7LfBLcCdwOFjNmXbnmiGeU"

                    }
                }

            ),
            201: openapi.Response(
                description="زمانی که کاربری که نام کاربری و رمز او را وارد کرده اید اکانت خود را وریفای نکرده باشد و کدی برای شماره او ارسال شده باشد کلید وریفای را به شما میدهد",
                examples={
                    "application/json": {"key": "EIZ1jcVqZmNfdIiEX5VrLcRmkcuOUucA4iz82mYV",
                                         "time": "2024-06-14T18:39:40.973550Z"}

                }
            ),
            204: openapi.Response(
                description="خطا در ارسال اس ام اس برای کاربر احراز هویت نشده .",
                examples={
                    "application/json": {
                        "error": "Your mobile number is not verified and I could not send the code. try again"
                    }
                }
            )
        },
    )
    def post(self, request):
        user = auth.authenticate_user(request.data)
        if not user:
            data = {
                'errors': {
                    'fa': ['ورود ناموفق! نام کاربری یا ایمیل رمز عبور اشتباه است!', ],
                    'en': ['Login failed! The username or email or password is incorrect!', ]
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if user.active_sessions_count() >= user.role.count_access_token:
            data = {
                'errors': {
                        'fa': ['ورود ناموفق! تعداد نشست های ممکن شما تکمیل شده است! لطفا ابتدا یکی را غیرفعال کنید تا امکان ورود جدید اضافه شود!', ],
                    'en': ['Login failed! You have reached the maximum number of active sessions. Please deactivate one before starting a new session!', ]
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'access': jwt.create_access_token(user),
            'refresh': jwt.create_refresh_token(user),
        }
        return Response(data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):

    @swagger_auto_schema(
        operation_description="ثبت نام .",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           ),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='ایمیل',
                                        ),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='رمز عبور',
                                           ),
                'password2': openapi.Schema(type=openapi.TYPE_STRING, description='تکرار رمز عبور',
                                            ),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='نام کامل',
                                            ),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='شماه همراه')            },
            required=['username', 'email', 'password', 'password2', 'full_name', 'phone']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در ثبت نام کاربر",
                examples={
                    "application/json": "Register Failed"
                }
            ),
            201: openapi.Response(
                description="ثبت موفق اطلاعات کاربر و برگرداندن اطلاعات کاربر به همراه کلید و تایم وریفای",
                examples={
                    "application/json": {
                        "user": {
                            "username": "mehdi_abbasid",
                            "email": "abasimahdi2445@gmail.com",
                            "password": "@Aa123456",
                            "password2": "@Aa123456",
                            "full_name": "میتی عبوسی",
                            "phone": "09132895065"
                        },
                        "key": "EIZ1jcVqZmNfdIiEX5VrLcRmkcuOUucA4iz82mYV",
                        "time": "2024-06-14T18:39:40.973550Z"
                    }

                }
            )
        },
    )
    def post(self, request):
        data = request.data
        serializer = CustomUserCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # sms_sended = SmsUserVerify.objects.filter(key=user[1]).first()
            return Response(data={
                'user': serializer.validated_data,
                # 'key': user[1],
                # 'time': sms_sended.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(data="Register Failed", status=status.HTTP_400_BAD_REQUEST)
