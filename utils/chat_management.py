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

    def join(self, id):
        chat_room = ChatRoom.objects.get(id=id)
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

    def messages(self, id, page_size, page):
        chat_room = ChatRoom.objects.get(id=id)
        if not chat_room:
            return status.HTTP_404_NOT_FOUND, None
        messages = chat_room.messages.filter(is_deleted=False).order_by('-date')
        if messages is not None:
            serializer = MessageSerializer(messages, many=True)
            return status.HTTP_200_OK, self.paginate_queryset(serializer.data, page_size, page)
        return status.HTTP_204_NO_CONTENT, None

    def paginate_queryset(self, queryset, page_size, page):
        page_count = len(queryset) // page_size + (1 if len(queryset) % page_size > 0 else 0)
        n = 0
        n2 = 0
        l = []
        while n < page_count:
            l2 = []
            n3 = 0
            while n3 < page_size:
                if n2 == len(queryset) - 1:
                    break
                l2.append(queryset[n2])
                n2 += 1
                n3 += 1
            l.append(l2)
            l2 = []
            n += 1
        if page >= len(l):
            return False, 'out of range'
        return True, l[page + 1]
