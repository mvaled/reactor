import json
import logging

from channels.db import database_sync_to_async as db
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.core.signing import Signer
from django.http.response import HttpResponse
from django.test import Client
from django.utils.datastructures import MultiValueDict

from . import serializer
from .repository import ComponentRepository
from .utils import parse_request_data

log = logging.getLogger("reactor")


class ReactorConsumer(AsyncJsonWebsocketConsumer):
    @property
    def user(self):
        return self.scope.get("user") or AnonymousUser()

    async def connect(self):
        await super().connect()
        self.subscriptions = set()
        self.repo = ComponentRepository(
            user=self.user,
            channel_name=self.channel_name,
        )

    # Fronted commands

    async def receive_json(self, content):
        await getattr(self, f'command_{content["command"]}')(
            **content["payload"]
        )

    async def command_join(self, name, state):
        state = json.loads(Signer().unsign(state))
        log.debug(f"<<< JOIN {name} {state}")
        component = await db(self.repo.join)(name, state)
        await self.send_render(component)
        await self.send_pending_messages()

    async def command_leave(self, id):
        log.debug(f"<<< LEAVE {id}")
        self.repo.remove(id)

    async def command_user_event(
        self, id, command, implicit_args, explicit_args
    ):
        kwargs = dict(
            parse_request_data(MultiValueDict(implicit_args)), **explicit_args
        )
        log.debug(f"<<< USER-EVENT {id} {command} {kwargs}")
        component = await db(self.repo.dispatch_event)(id, command, kwargs)
        await self.send_render(component)
        await self.send_pending_messages()

    # Componet commands

    async def message_from_component(self, data):
        await getattr(self, f"component_{data['command']}")(**data["kwargs"])

    async def component_remove(self, id):
        log.debug(f">>> REMOVE {id}")
        await self.send_command("remove", {"id": id})

    async def component_focus_on(self, selector):
        log.debug(f'>>> FOCUS ON "{selector}"')
        await self.send_command("focus_on", {"selector": selector})

    async def component_redirect_to(self, url: str, replace: bool = False):
        action = "REPLACE WITH" if replace else "REDIRECT TO"
        log.debug(f'>>> {action} "{url}"')
        await self.send_command("visit", {"url": url, "replace": replace})

    async def component_push_page(self, url: str):
        try:
            log.debug(f'>>> PUSH PAGE "{url}"')
            client = Client()
            if not isinstance(self.user, AnonymousUser):
                await db(client.force_login)(self.user)
            response: HttpResponse = await db(client.get)(
                url,
                follow=True,
            )
            if response.redirect_chain:
                page_url, _status = response.redirect_chain[-1]
            else:
                page_url = url
            await self.send_command(
                "page",
                {
                    "url": page_url,
                    "content": response.content.decode().strip(),
                },
            )
        except Exception as e:
            log.debug(f'>>> PUSH FAILED "{e}"')
            await self.component_redirect_to(url)

    # Incoming messages from subscriptions

    async def model_mutation(self, data):
        # The signature here is coupled to:
        #   `reactor.auto_broadcast.notify_mutation`
        await self._dispatch_notifications(
            "mutation",
            data["channel"],
            {
                "instance": serializer.decode(data["instance"]),
                "action": data["action"],
            },
        )

    async def notification(self, data):
        # The signature here is coupled to:
        #   `reactor.component.broadcast`
        await self._dispatch_notifications(
            "notification", data["channel"], data["kwargs"]
        )

    async def _dispatch_notifications(self, receiver, channel, kwargs):
        for component in self.repo.components_subscribed_to(channel):
            await db(getattr(component, receiver))(channel, **kwargs)
            await self.send_render(component)
        await self.send_pending_messages()

    # Reply to frontned

    async def send_render(self, component):
        diff = await db(component.render_diff)(self.repo)
        if diff is not None:
            log.debug(f">>> RENDER {component._name} {component.id}")
            await self.send_command(
                "render",
                {"id": component.id, "diff": diff},
            )

    async def send_command(self, command, payload):
        await self.send_json({"command": command, "payload": payload})

    async def send_pending_messages(self):
        await self.check_subscriptions()
        for channel, command, kwargs in self.repo.messages_to_send:
            await self.channel_layer.send(
                channel,
                {
                    "type": "message_from_component",
                    "command": command,
                    "kwargs": kwargs,
                },
            )

    async def check_subscriptions(self):
        subscriptions = self.repo.subscriptions

        # new subscriptions
        for channel in subscriptions - self.subscriptions:
            log.debug(f"::: SUBSCRIBE {self.channel_name} to {channel}")
            await self.channel_layer.group_add(channel, self.channel_name)

        # remove subscriptions
        for channel in self.subscriptions - subscriptions:
            log.debug(f"::: UNSUBSCRIBE {self.channel_name} to {channel}")
            await self.channel_layer.group_discard(channel, self.channel_name)

        self.subscriptions = subscriptions
