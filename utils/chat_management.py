from django.db.models.expressions import result

from user.models import CustomUser
from chat.models import ChatRoom, Participant, Message
from django.db.models import Q, Count, OuterRef, Subquery
from chat.serializers import ChatRoomSerializer, MessageSerializer, ChatRoomListSerializer
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
        def paginate_queryset(queryset, page_size, last_ms_id=None):
            b = 0
            queryset = list(queryset)
            while b < len(queryset):
                c = b + 1
                while c < len(queryset):
                    if queryset[c].last_message_date:
                        if queryset[b].last_message_date:
                            if queryset[c].last_message_date > queryset[b].last_message_date:
                                queryset[b], queryset[c] = queryset[c], queryset[b]
                        else:
                            if queryset[c].last_message_date > queryset[b].updated_at:
                                queryset[b], queryset[c] = queryset[c], queryset[b]
                    else:
                        if queryset[b].last_message_date:
                            if queryset[c].updated_at > queryset[b].last_message_date:
                                queryset[b], queryset[c] = queryset[c], queryset[b]
                        else:
                            if queryset[c].updated_at > queryset[b].updated_at:
                                queryset[b], queryset[c] = queryset[c], queryset[b]
                    c += 1
                b += 1
            result = []
            if last_ms_id:
                flag = False
                for q in queryset:
                    if q.id == last_ms_id:
                        flag = True
                        break
                    if not flag:
                        result.append(q)
                if not flag:
                    return False, None
                if len(result) > page_size:
                    result = result[len(result) - page_size:]
            else:
                if len(queryset) > page_size:
                    result = queryset[len(queryset) - 1 - page_size:]
                else:
                    result = queryset
            return True, result
        last_message_subquery = Message.objects.filter(
            chat=OuterRef('pk')
        ).order_by('-date').values(
            'text',
            'date',
            'sender__username',
            'message_type'
        )[:1]
        chat_rooms = ChatRoom.objects.filter(participants__user=self.user).distinct().annotate(
            unread_count=Count('messages', distinct=True,
                               filter=Q(~Q(messages__sender=self.user) & ~Q(messages__message_views__user=self.user))),
            last_message_date=Subquery(last_message_subquery.values('date')),
            last_message_text=Subquery(last_message_subquery.values('text')),
            last_message_sender=Subquery(last_message_subquery.values('sender__username')),
            last_message_type=Subquery(last_message_subquery.values('message_type'))
        ).order_by('-last_message_date')
        chat_rooms = paginate_queryset(chat_rooms, page_size, last_chat_room_id)
        if not chat_rooms[0]:
            return status.HTTP_404_NOT_FOUND, None
        request.user = self.user
        serializer = ChatRoomListSerializer(
            chat_rooms[1],
            many=True,
            context={'request': request}  # مهم برای دسترسی به کاربر در سریالایزر
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

    def join(self, id):  # باید تست بشه
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
