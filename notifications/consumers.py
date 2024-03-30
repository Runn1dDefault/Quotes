import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


class AsyncNotificationConsumer(AsyncWebsocketConsumer):
    room = settings.NOTIFICATION_ROOM
    ERRORS = {
        "default_message": _("Something went wrong!"),
        "receive_not_implement": _("You cannot send anything to this room!")
    }

    async def connect(self):
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def send_error_message(self, reason_key=None, reason=None):
        if reason_key:
            reason = self.ERRORS[reason_key]
        elif not reason:
            reason = self.ERRORS["default_message"]

        await self.channel_layer.group_send(
            self.room,
            {'type': 'send_message', 'data': {"type": "error", "reason": force_str(reason)}}
        )

    async def receive(self, text_data=None, bytes_data=None):
        await self.send_error_message(reason_key="receive_not_implement")
