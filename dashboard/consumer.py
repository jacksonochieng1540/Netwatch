import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    GROUP = 'dashboard'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if json.loads(text_data or '{}').get('type') == 'ping':
                await self.send(json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            pass

    async def device_update(self, event):
        await self.send(json.dumps({'type': 'device_update', 'data': event['data']}))

    async def alert_fired(self, event):
        await self.send(json.dumps({'type': 'alert', 'data': event['data']}))
