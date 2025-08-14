from django.contrib import admin
from chat.models import *


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'sender', 'sender_chat', 'message_type', 'text', 'date']



@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'username', 'type']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'chat', 'role']


@admin.register(MessageView)
class MessageViewAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'user', 'view_date']
