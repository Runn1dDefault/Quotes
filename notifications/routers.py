from django.urls import path

from notifications.consumers import AsyncNotificationConsumer


websocket_urlpatterns = [
    path("ws/notifications", AsyncNotificationConsumer.as_asgi()),
]
