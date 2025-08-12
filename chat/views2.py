from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import (
    ChatRoom, Participant, Message, MessageReaction,
    StickerPack, Sticker, GIF, MessageView,
    StickerUsage, GIFUsage, UserStickerCollection,
    AdminLog, ChatSettings
)
from .serializers import (
    ChatRoomSerializer, ParticipantSerializer,
    MessageSerializer, MessageReactionSerializer,
    StickerPackSerializer, StickerSerializer,
    GIFSerializer, AdminLogSerializer
)
from .signals import message_created
from .permissions import IsChatParticipant, IsChatAdmin, IsMessageSender

User = get_user_model()


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # فقط چت‌هایی که کاربر در آن‌ها عضو است
        return ChatRoom.objects.filter(
            participants__user=self.request.user
        ).distinct().annotate(
            member_count=Count('participants', distinct=True)
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        chat = serializer.save(creator=self.request.user)
        # ایجاد نقش مالک برای سازنده
        Participant.objects.create(
            chat=chat,
            user=self.request.user,
            role='OW',
            permissions=['all']
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        chat = self.get_object()
        if chat.is_public or chat.join_by_request:
            participant, created = Participant.objects.get_or_create(
                chat=chat,
                user=request.user,
                defaults={'role': 'ME'}
            )
            if created:
                return Response({'status': 'joined'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'already_joined'}, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Cannot join this chat'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        messages = chat.messages.filter(is_deleted=False).order_by('-date')
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(
            messages, many=True, context={'request': request}
        )
        return Response(serializer.data)


class ParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatAdmin]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Participant.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        chat = ChatRoom.objects.get(id=self.kwargs['chat_id'])
        serializer.save(chat=chat)

    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None, chat_id=None):
        participant = self.get_object()
        # منطق ارتقای کاربر به ادمین
        return Response({'status': 'promoted'})

    @action(detail=True, methods=['post'])
    def mute(self, request, pk=None, chat_id=None):
        participant = self.get_object()
        # منطق سکوت کردن کاربر
        return Response({'status': 'muted'})


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.filter(is_deleted=False)
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        return self.queryset.filter(
            chat_id=self.kwargs['chat_id']
        ).order_by('-date')

    def perform_create(self, serializer):
        chat = ChatRoom.objects.get(id=self.kwargs['chat_id'])
        message = serializer.save(
            chat=chat,
            sender=self.request.user
        )
        # ارسال سیگنال برای ایجاد نوتیفیکیشن
        message_created.send(sender=Message, instance=message)

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None, chat_id=None):
        message = self.get_object()
        # منطق سنجاق کردن پیام
        return Response({'status': 'pinned'})

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None, chat_id=None):
        message = self.get_object()
        emoji = request.data.get('emoji')
        sticker_id = request.data.get('sticker_id')

        # ایجاد یا به‌روزرسانی واکنش
        reaction, created = MessageReaction.objects.update_or_create(
            message=message,
            user=request.user,
            defaults={
                'emoji': emoji,
                'sticker_id': sticker_id
            }
        )
        return Response(
            MessageReactionSerializer(reaction).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None, chat_id=None):
        message = self.get_object()
        device = request.META.get('HTTP_USER_AGENT', '')

        # ثبت مشاهده پیام
        view, created = MessageView.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'device': device[:100]}
        )

        if created:
            message.views += 1
            message.save()

        return Response({'status': 'viewed'})


class StickerPackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StickerPack.objects.filter(is_public=True)
    serializer_class = StickerPackSerializer

    @action(detail=True, methods=['post'])
    def add_to_collection(self, request, pk=None):
        sticker_pack = self.get_object()
        UserStickerCollection.objects.get_or_create(
            user=request.user,
            pack=sticker_pack
        )
        return Response({'status': 'added'})

    @action(detail=True, methods=['post'])
    def remove_from_collection(self, request, pk=None):
        sticker_pack = self.get_object()
        UserStickerCollection.objects.filter(
            user=request.user,
            pack=sticker_pack
        ).delete()
        return Response({'status': 'removed'})

    @action(detail=False, methods=['get'])
    def my_collection(self, request):
        packs = StickerPack.objects.filter(
            user_collections__user=request.user
        )
        serializer = self.get_serializer(packs, many=True)
        return Response(serializer.data)


class GIFViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GIF.objects.all()
    serializer_class = GIFSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        gifs = GIF.objects.filter(
            Q(title__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:20]
        serializer = self.get_serializer(gifs, many=True)
        return Response(serializer.data)


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatAdmin]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return AdminLog.objects.filter(chat_id=chat_id).order_by('-date')

# ویوهای مشابه برای سایر مدل‌ها