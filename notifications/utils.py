from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings


def send_notification(message: str, **extra_data):
    channel_layer = get_channel_layer()
    event = {'type': 'send_message', 'data': {"type": "notification", "text": message, **extra_data}}
    async_to_sync(channel_layer.group_send)(settings.NOTIFICATION_ROOM, event)
