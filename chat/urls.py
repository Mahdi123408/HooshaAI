from django.urls import path
from chat import views

urlpatterns = [
    path('/<int:chat_id>/messages/<int:page_size>', views.MessageAPIView.as_view(), name='chat-messages'),

    path('/<int:chat_id>/messages/<int:page_size>/<int:last_ms_id>', views.MessageAPIView.as_view(),
         name='chat-messages-paginated-with-last-ms-id'),
    path('/chatrooms/<int:page_size>', views.ChatRoomAPIView.as_view(),
         name='chat-rooms'),
    path('/chatrooms/<int:page_size>/<int:last_chat_room_id>', views.ChatRoomAPIView.as_view(),
         name='chat-rooms-paginated-with-last-chat-room-id'),
    path('/chatrooms/join/<int:id>', views.ChatRoomAPIView.as_view(),
         name='chat-rooms-public-join-with-chat-room-id'),
    path('/chatrooms/join/<int:id>/<str:join_hash>', views.ChatRoomAPIView.as_view(),
         name='chat-rooms-private-join-with-chat-room-id-and-join-hash'),
]