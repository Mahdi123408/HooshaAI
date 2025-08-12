from django.urls import path
from chat import views

urlpatterns = [
    path('/<int:chat_id>/messages/<int:page_size>/', views.MessageAPIView.as_view(), name='chat-messages'),

    path('/<int:chat_id>/messages/<int:page_size>/<int:last_ms_id>/', views.MessageAPIView.as_view(),
         name='chat-messages-paginated'),
]