from pyexpat.errors import messages
from rest_framework import serializers
from .models import (
    User, ChatRoom, Participant, Message,
    StickerPack, Sticker, GIF, MessageReaction,
    MessageView, StickerUsage, GIFUsage,
    UserStickerCollection, AdminLog
)
from user.models import CustomUser
from authentication.serializers import UserViewSerializer
from django.utils import timezone
from datetime import timedelta

# class UserSerializer(serializers.ModelSerializer):
#     online_status = serializers.BooleanField(read_only=True)
#     last_seen = serializers.DateTimeField(read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name',
#                   'avatar', 'online_status', 'last_seen']


class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = ['id', 'file', 'format', 'emoji', 'width', 'height',
                  'frame_rate', 'duration', 'file_size', 'usage_count']


class StickerPackSerializer(serializers.ModelSerializer):
    stickers = StickerSerializer(many=True, read_only=True)
    creator = UserViewSerializer(read_only=True)
    is_added = serializers.SerializerMethodField()

    class Meta:
        model = StickerPack
        fields = ['id', 'title', 'identifier', 'creator', 'pack_type',
                  'is_animated', 'is_video', 'is_emoji', 'is_official',
                  'is_public', 'premium', 'usage_count', 'downloads',
                  'rating', 'thumbnail', 'stickers', 'is_added']

    def get_is_added(self, obj):
        user = self.context['request'].user
        return UserStickerCollection.objects.filter(
            user=user, pack=obj
        ).exists()


class GIFSerializer(serializers.ModelSerializer):
    class Meta:
        model = GIF
        fields = ['id', 'title', 'file', 'thumbnail', 'width', 'height',
                  'duration', 'frame_rate', 'file_size', 'usage_count',
                  'source', 'attribution']


class ChatRoomSerializer(serializers.ModelSerializer):
    creator = UserViewSerializer(read_only=True)
    participants_count = serializers.IntegerField(source='member_count', read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'username', 'description', 'type',
                  'creator', 'created_at', 'avatar', 'is_public',
                  'participants_count', 'unread_count', 'last_message']

    def get_unread_count(self, obj):
        user = self.context['request'].user
        last_seen = user.chat_seen_dates.filter(chat=obj).first()
        if last_seen:
            return obj.messages.filter(date__gt=last_seen.last_seen).count()
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(is_deleted=False).last()
        if last_msg:
            return MessageSerializer(last_msg, context=self.context).data
        return None





class ParticipantSerializer(serializers.ModelSerializer):
    user = UserViewSerializer(read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Participant
        fields = ['id', 'user', 'role', 'permissions', 'custom_title',
                  'is_muted', 'can_send_messages', 'can_send_media',
                  'can_send_stickers', 'can_send_gifs', 'joined_date']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserViewSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), allow_null=True)
    reactions = serializers.SerializerMethodField()
    # is_viewed = serializers.SerializerMethodField()
    sticker = StickerSerializer(read_only=True)
    gif = GIFSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'message_type', 'text', 'caption',
                  'media_file', 'media_thumbnail', 'sticker', 'gif', 'parent',
                  'is_pinned', 'is_edited', 'edit_date', 'views', 'forwards',
                  'date', 'has_spoiler', 'reactions']

    def get_reactions(self, obj):
        return MessageReactionSerializer(
            obj.reactions.all(), many=True
        ).data

    # def get_is_viewed(self, obj):
    #     user = self.context['request'].user
    #     return obj.views.filter(user=user).exists()


class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserViewSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'emoji', 'sticker', 'date']


class AdminLogSerializer(serializers.ModelSerializer):
    actor = UserViewSerializer(read_only=True)
    target_user = UserViewSerializer(read_only=True)

    class Meta:
        model = AdminLog
        fields = ['id', 'chat', 'actor', 'action', 'target_user', 'details', 'date']


class StickerUsageSerializer(serializers.ModelSerializer):
    sticker = StickerSerializer(read_only=True)

    class Meta:
        model = StickerUsage
        fields = ['id', 'sticker', 'chat', 'usage_date']


class LastMessageSerializer(serializers.Serializer):
    text = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='last_message_date')
    sender = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()
    type = serializers.CharField(source='last_message_type')
    is_media = serializers.SerializerMethodField()

    def get_text(self, obj):
        """خلاصه‌سازی متن بر اساس نوع پیام"""
        if obj.last_message_type != 'text':
            return self._get_media_summary(obj.last_message_type)
        return obj.last_message_text[:40] + '...' if len(obj.last_message_text) > 40 else obj.last_message_text

    def get_sender(self, obj):
        """نام فرستنده یا 'شما' اگر خود کاربر باشد"""
        if obj.last_message_sender == self.context['request'].user:
            return {
                'en':'you',
                'fa': 'شما'
            }
        return obj.last_message_sender

    def get_sender_avatar(self, obj):
        """آدرس آواتار فرستنده"""
        if obj.last_message_sender:
            user = CustomUser.objects.filter(username=obj.last_message_sender, is_active=True).first()
            if user and user.avatar_url:
                return user.avatar_url.url
        return None

    def get_is_media(self, obj):
        """آیا پیام از نوع رسانه است؟"""
        return obj.last_message_type not in ['text', 'poll']

    def _get_media_summary(self, msg_type):
        """توضیح خلاصه برای انواع رسانه"""
        media_types = {
            'photo': {'fa':'📷 عکس', 'en':'photo 📷'},
            'video': {'fa':'🎬 ویدیو', 'en':'video 🎬'},
            'voice': {'fa':'🎧 پیام صوتی', 'en':'voice 🎧'},
            'sticker': {'fa':'🖼️ استیکر', 'en':'sticker 🖼️'},
            'gif': 'GIF',
            'document': {'fa':'📄 سند', 'en':'document 📄️'},
            'contact': {'fa':'👤 مخاطب', 'en':'contact 👤️'},
        }
        return media_types.get(msg_type, {'fa':'پیام', 'en':'message'})

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # بررسی وجود پیام
        has_messages = Message.objects.filter(
            chat__id=instance.id,
            is_deleted=False
        ).exists()

        if not has_messages:
            data = None

        return data


class ChatRoomListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField()
    unread_count = serializers.IntegerField(read_only=True)
    last_message = LastMessageSerializer(source='*', read_only=True)
    is_online = serializers.SerializerMethodField()
    is_group = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()  # فقط برای چت‌های خصوصی

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'name',
            'type',
            'avatar',
            'member_count',
            'unread_count',
            'last_message',
            'is_online',
            'is_group',
            'other_user',  # اطلاعات کاربر مقابل در چت خصوصی
            'updated_at'
        ]

    def get_is_online(self, obj):
        """بررسی آنلاین بودن آخرین فرستنده"""
        if not hasattr(obj, 'last_message_sender') or not obj.last_message_sender:
            return False
        user = CustomUser.objects.filter(username=obj.last_message_sender, is_active=True).first()
        if not user:
            return False
        return user.is_online

    def get_is_group(self, obj):
        """آیا چت روم یک گروه است؟"""
        return obj.type in ['GP', 'CH', 'BC']

    def get_other_user(self, obj):
        """اطلاعات کاربر مقابل در چت خصوصی"""
        if obj.type != 'PV':
            return None

        request = self.context.get('request')
        if not request or not request.user:
            return None

        # پیدا کردن کاربر مقابل در چت خصوصی
        other_user = obj.participants.exclude(user=request.user).first()
        if not other_user:
            return None

        return {
            'id': other_user.user.id,
            'username': other_user.user.username,
            'full_name': other_user.user.full_name,
            'avatar': other_user.user.avatar_url.url if other_user.user.avatar_url else None
        }

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField()
    is_online = serializers.SerializerMethodField()
    is_group = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()  # فقط برای چت‌های خصوصی

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'name',
            'type',
            'avatar',
            'member_count',
            'is_online',
            'is_group',
            'other_user',  # اطلاعات کاربر مقابل در چت خصوصی
            'updated_at'
        ]

    def get_is_online(self, obj):
        """بررسی آنلاین بودن آخرین فرستنده"""
        if not hasattr(obj, 'last_message_sender') or not obj.last_message_sender:
            return False
        user = CustomUser.objects.filter(username=obj.last_message_sender, is_active=True).first()
        if not user:
            return False
        return user.is_online

    def get_is_group(self, obj):
        """آیا چت روم یک گروه است؟"""
        return obj.type in ['GP', 'CH', 'BC']

    def get_other_user(self, obj):
        """اطلاعات کاربر مقابل در چت خصوصی"""
        if obj.type != 'PV':
            return None

        request = self.context.get('request')
        if not request or not request.user:
            return None

        # پیدا کردن کاربر مقابل در چت خصوصی
        other_user = obj.participants.exclude(user=request.user).first()
        if not other_user:
            return None

        return {
            'id': other_user.user.id,
            'username': other_user.user.username,
            'full_name': other_user.user.full_name,
            'avatar': other_user.user.avatar_url.url if other_user.user.avatar_url else None
        }

class ParticipantPVSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'user', 'chat', 'role']