from django.db import models
from user.models import CustomUser
#
# class ChatRoom(models.Model):
#     name = models.CharField(max_length=255)
#     participants = models.ManyToManyField(CustomUser, related_name='chat_rooms')
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_group = models.BooleanField(default=False)
#     is_group
#
# class Message(models.Model):
#     room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
#     sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     read_by = models.ManyToManyField(CustomUser, related_name='read_messages', blank=True)
