from rest_framework import serializers
from .models import (
    User, ChatRoom, Participant, Message,
    StickerPack, Sticker, GIF, MessageReaction,
    MessageView, StickerUsage, GIFUsage,
    UserStickerCollection, AdminLog
)
from authentication.serializers import UserViewSerializer

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

# سریالایزرهای مشابه برای سایر مدل‌ها