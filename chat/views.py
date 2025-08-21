from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpRequest
from authentication import auth
from HooshaAI.settings import CUSTOM_ACCESS_TOKEN_NAME
from rest_framework.response import Response
from rest_framework import status
from utils.chat_management import ChatManagementByDB


class MessageAPIView(APIView):

    @swagger_auto_schema(
        operation_description="برگرداندن پیام های چت روم کاربر .",
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
    def get(self, request: HttpRequest, chat_id, page_size, last_ms_id=None):
        user = auth.get_authenticated_user_from_request(request)
        if not user:
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
        chat = ChatManagementByDB(user)
        try:
            page_size = int(page_size)
            if page_size <= 0:
                data = {
                    'errors': {
                        'fa': [
                            'تعداد پیام مورد درخواست باید مثبت باشد !',
                        ],
                        'en': [
                            'page_size must be greater than 0 !',
                        ]
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            data = {
                'errors': {
                    'fa': [
                        'تعداد پیام مورد درخواست باید عدد صحیح باشد !',
                    ],
                    'en': [
                        'page_size must be an integer !',
                    ]
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        try:
            chat_id = int(chat_id)
            if chat_id <= 0:
                data = {
                    'errors': {
                        'fa': [
                            'آیدی چت روم مورد درخواست باید مثبت باشد !',
                        ],
                        'en': [
                            'chat_id must be greater than 0 !',
                        ]
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            data = {
                'errors': {
                    'fa': [
                        'آیدی چت روم مورد درخواست باید عدد صحیح باشد !',
                    ],
                    'en': [
                        'chat_id must be an integer !',
                    ]
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if last_ms_id:
            try:
                last_ms_id = int(last_ms_id)
                if last_ms_id <= 0:
                    data = {
                        'errors': {
                            'fa': [
                                'آیدی آخرین پیام مورد درخواست باید مثبت باشد !',
                            ],
                            'en': [
                                'last_ms_id must be greater than 0 !',
                            ]
                        }
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                data = {
                    'errors': {
                        'fa': [
                            'آیدی آخرین پیام مورد درخواست باید عدد صحیح باشد !',
                        ],
                        'en': [
                            'page_size must be an integer !',
                        ]
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        messages = chat.messages(chat_id, page_size, last_ms_id)
        return Response(messages[1], status=messages[0])


class ChatRoomAPIView(APIView):

    @swagger_auto_schema(
        operation_description="برگرداندن چت روم های کاربر .",
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
    def get(self, request: HttpRequest, page_size, last_chat_room_id=None):
        user = auth.get_authenticated_user_from_request(request)
        if not user:
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
        chat = ChatManagementByDB(user)
        try:
            page_size = int(page_size)
            if page_size <= 0:
                data = {
                    'errors': {
                        'fa': [
                            'تعداد چت مورد درخواست باید مثبت باشد !',
                        ],
                        'en': [
                            'page_size must be greater than 0 !',
                        ]
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            data = {
                'errors': {
                    'fa': [
                        'تعداد چت مورد درخواست باید عدد صحیح باشد !',
                    ],
                    'en': [
                        'page_size must be an integer !',
                    ]
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if last_chat_room_id is not None:
            try:
                last_chat_room_id = int(last_chat_room_id)
                if last_chat_room_id <= 0:
                    data = {
                        'errors': {
                            'fa': [
                                'آیدی آخرین چت مورد درخواست باید مثبت باشد !',
                            ],
                            'en': [
                                'last_chat_room_id must be greater than 0 !',
                            ]
                        }
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                data = {
                    'errors': {
                        'fa': [
                            'آیدی آخرین چت مورد درخواست باید عدد صحیح باشد !',
                        ],
                        'en': [
                            'last_chat_room_id must be an integer !',
                        ]
                    }
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        chat_rooms = chat.get_chat_rooms(page_size, last_chat_room_id, request)
        return Response(chat_rooms[1], status=chat_rooms[0])

    @swagger_auto_schema(
        operation_description="عضو شدن کابر در یک چت روم توسط خودش یعنی یا باید پابلیک باشه یا لینک دعوت داشته باشه .",
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
    def post(self, request: HttpRequest, id, join_hash=None):
        user = auth.get_authenticated_user_from_request(request)
        if not user:
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
        chat = ChatManagementByDB(user)
        result = chat.join(id, join_hash)
        return Response(data=result[1], status=result[0])

