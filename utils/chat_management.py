from user.models import CustomUser
from chat.models import ChatRoom, Participant
from django.db.models import Q, Count
from chat.serializers import ChatRoomSerializer, MessageSerializer
from rest_framework import status


class ChatManagementByDB:
    def __init__(self, user: CustomUser):
        self.user = user

    def get_chat_rooms(self):
        chat_rooms = ChatRoom.objects.filter(participants__user=self.user).distinct().annotate(
            member_count=Count('participants', distinct=True)).order_by('-updated_at')
        return chat_rooms

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

    def join(self, id): # باید تست بشه
        chat_room = ChatRoom.objects.filter(id=id).first()
        if not chat_room:
            return status.HTTP_404_NOT_FOUND
        if chat_room.is_public or chat_room.join_by_request:
            participant, created = Participant.objects.get_or_create(
                chat=chat_room,
                user=self.user,
                defaults={'role': 'ME'}
            )
            if created:
                return status.HTTP_201_CREATED
            return status.HTTP_200_OK
        return status.HTTP_403_FORBIDDEN

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
