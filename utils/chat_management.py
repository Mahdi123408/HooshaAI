from django.db.models.expressions import result

from user.models import CustomUser
from chat.models import ChatRoom, Participant, Message
from django.db.models import Q, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce


from chat.serializers import ChatRoomSerializer, MessageSerializer, ChatRoomListSerializer, ParticipantPVSerializer, \
    ChatRoomCreateSerializer
from rest_framework import status


class ChatManagementByDB:
    def __init__(self, user: CustomUser):
        self.user = user

    def get_count_unread_ms(self, chatroom: ChatRoom) -> int:  # باید تست بشه
        unread_count = Message.objects.filter(
            chat=chatroom
        ).exclude(
            Q(sender=self.user) |
            Q(message_views__user=self.user)
        ).count()

        return unread_count


    def get_chat_rooms(self, page_size, last_chat_room_id=None, request=None):
        queryset = ChatRoom.objects.filter(
            participants__user=self.user
        ).distinct().annotate(
            unread_count=Count(
                'messages',
                distinct=True,
                filter=Q(~Q(messages__sender=self.user) & ~Q(messages__message_views__user=self.user))
            ),
            effective_order_date=Coalesce('last_message_date', 'updated_at')
        ).select_related('last_message', 'last_message__sender')

        if last_chat_room_id:
            # گرفتن آخرین چت با annotate
            try:
                last_chat_room = ChatRoom.objects.filter(pk=last_chat_room_id).annotate(
                    effective_order_date=Coalesce('last_message_date', 'updated_at')
                ).get()
                queryset = queryset.filter(
                    Q(effective_order_date__gt=last_chat_room.effective_order_date) |
                    Q(effective_order_date=last_chat_room.effective_order_date, id__gt=last_chat_room.id)
                )
            except ChatRoom.DoesNotExist:
                # اگر آخرین چت پیدا نشد، ادامه از ابتدا
                pass

        queryset = queryset.order_by('-effective_order_date', '-id')

        chat_rooms = list(queryset[:page_size])

        if not chat_rooms:
            return status.HTTP_404_NOT_FOUND, None

        request.user = self.user
        serializer = ChatRoomListSerializer(
            chat_rooms,
            many=True,
            context={'request': request}
        )
        return status.HTTP_200_OK, serializer.data

    def create_gpy_chat_room(self, serializer: ChatRoomSerializer):
        chat = serializer.save(creator=self.user)
        # ایجاد نقش مالک برای سازنده
        Participant.objects.create(
            chat=chat,
            user=self.user,
            role='OW',
            permissions=['all']
        )
        return chat

    def join(self, id, join_hash=None):
        chat_room = ChatRoom.objects.filter(id=id).exclude(Q(type='PV')).first()
        if not chat_room:
            data = {
                'errors': {
                    'fa': [
                        'چت پیدا نشد !',
                    ],
                    'en': [
                        'chat not found !',
                    ]
                }
            }
            return status.HTTP_404_NOT_FOUND, data
        if chat_room.is_public or chat_room.join_by_request and chat_room.invite_link == join_hash:

            participant, created = Participant.objects.get_or_create(
                chat=chat_room,
                user=self.user,
                defaults={'role': 'ME'}
            )
            if created:
                chat_room.member_count += 1
                chat_room.save()
                return status.HTTP_201_CREATED, None
            return status.HTTP_200_OK, None
        return status.HTTP_403_FORBIDDEN, None

    def create_pv_chat_room(self, username, request):
        to_user = CustomUser.objects.filter(username=username, is_active=True, can_message_me=True).first()
        if not to_user:
            data = {
                'errors': {
                    'fa': [
                        'کاربر پیدا نشد !',
                    ],
                    'en': [
                        'user not found !',
                    ]
                }
            }
            return status.HTTP_404_NOT_FOUND, data
        chat_room = ChatRoom.objects.filter(
            type='PV',
            participants__user=self.user
        ).filter(
            participants__user=to_user
        ).first()
        if chat_room:
            return status.HTTP_409_CONFLICT, None
            # participant = Participant.objects.filter(user=self.user, chat__type='PV')
            # if participant:
            #
            # if len(participant) == 2:
            #     return status.HTTP_409_CONFLICT, None
            # elif len(participant) == 1 and participant[0].user.id == self.user.id:
            #     role = 'OW' if participant[0].role != 'OW' else 'ME'
            #     data_p = {
            #         'user': to_user,
            #         'role': role,
            #         'chat': chat_room
            #     }
            #     serializer_participant = ParticipantPVSerializer(data=data_p)
            #     if serializer_participant.is_valid(raise_exception=True):
            #         serializer_participant.save()
            #         serializer = ParticipantPVSerializer(data=participant)
            #         return status.HTTP_200_OK, serializer.validated_data
            # elif len(participant) == 1 and participant[0].user.id == to_user.id:
            #     role = 'OW' if participant[0].role != 'OW' else 'ME'
            #     data_p = {
            #         'user': self.user,
            #         'role': role,
            #         'chat': chat_room
            #     }
            #     serializer_participant = ParticipantPVSerializer(data=data_p)
            #     if serializer_participant.is_valid(raise_exception=True):
            #         serializer_participant.save()
            #         serializer = ParticipantPVSerializer(data=participant)
            #         return status.HTTP_200_OK, serializer.validated_data
            # elif not participant:
            #     data_p = [
            #         {
            #             'user': self.user,
            #             'role': 'OW',
            #             'chat': chat_room
            #         },
            #         {
            #             'user': to_user,
            #             'role': 'ME',
            #             'chat': chat_room
            #         }
            #     ]
            #     serializer_participant = ParticipantPVSerializer(data=data_p, many=True)
            #     if serializer_participant.is_valid(raise_exception=True):
            #         serializer_participant.save()
            #         return status.HTTP_200_OK, serializer_participant.validated_data[1]
            # else:
            #     return status.HTTP_403_FORBIDDEN, None
        data = {
            'name': f'PV_{self.user.id}_to_{to_user.id}',
            'description': f'PV_{self.user.id}_to_{to_user.id}',
            'type': 'PV',
            'creator': self.user,
            'member_count': 2
        }
        request.user = self.user
        serializer = ChatRoomCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            chat_room_new = serializer.save()
            data_p = [
                {
                    'user': self.user.id,
                    'role': 'OW',
                    'chat': chat_room_new.id
                },
                {
                    'user': to_user.id,
                    'role': 'ME',
                    'chat': chat_room_new.id
                }
            ]
            serializer_participant = ParticipantPVSerializer(data=data_p, many=True)
            if serializer_participant.is_valid(raise_exception=True):
                serializer_participant.save()
                result = self.get_chat_rooms(1, chat_room_new.id - 1, request)
                return status.HTTP_201_CREATED, result[1]
        return status.HTTP_403_FORBIDDEN, None

    def add(self):  # تابعی برای اضافه کردن کاربران به گروه یا چنل ( چون توی متد جوین یوزر درخواست میده که بپیونده و حتما باید یا پابلیک باشه اون چت یا باید لینک دعوت داشته باشه
        ...

    def messages(self, id, page_size, last_ms_id):
        chat_room = ChatRoom.objects.filter(id=id).first()
        if not chat_room:
            data = {
                'errors': {
                    'fa': [
                        'چت پیدا نشد !',
                    ],
                    'en': [
                        'chat not found !',
                    ]
                }
            }
            return status.HTTP_404_NOT_FOUND, data

        if not Participant.objects.filter(chat=chat_room, user=self.user).exists():
            data = {
                'errors': {
                    'fa': [
                        'شما به این چت دسترسی ندارید !',
                    ],
                    'en': [
                        'You do not have access to this chat !',
                    ]
                }
            }
            return status.HTTP_403_FORBIDDEN, data
        messages = chat_room.messages.filter(is_deleted=False)
        if messages is not None:
            messages = self.paginate_queryset(messages, page_size, last_ms_id)
            if not messages[0]:
                data = {
                    'errors': {
                        'fa': [
                            'پیام پیدا نشد !',
                        ],
                        'en': [
                            'message not found !',
                        ]
                    }
                }
                return status.HTTP_404_NOT_FOUND, data
            serializer = MessageSerializer(messages[1], many=True)
            return status.HTTP_200_OK, serializer.data
        return status.HTTP_204_NO_CONTENT, None

    def paginate_queryset(self, queryset, page_size, last_ms_id=None):
        """
        صفحه‌بندی بهینه پیام‌ها با یک کوئری
        """
        if last_ms_id:
            try:
                last_msg = queryset.only('id', 'date').get(id=last_ms_id)
            except queryset.model.DoesNotExist:
                return False, None

            messages = (
                queryset
                .filter(
                    Q(date__lt=last_msg.date) |
                    Q(date=last_msg.date, id__lt=last_msg.id)
                )
                .order_by('-date', '-id')[:page_size]
            )
        else:
            messages = queryset.order_by('-date', '-id')[:page_size]

        return True, messages
