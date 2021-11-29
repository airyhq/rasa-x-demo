import inspect
import logging
import os
import time
from asyncio import CancelledError
from typing import Text, Dict, Any, Optional, Callable, Awaitable, List

import requests
from rasa.core.channels import UserMessage, InputChannel
from rasa.core.channels.channel import OutputChannel
from rasa.server import update_conversation_with_events
from rasa.shared.core.events import AgentUttered, BotUttered
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

try:
    from urlparse import urljoin  # pytype: disable=import-error
except ImportError:
    from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class AiryBot(OutputChannel):

    @classmethod
    def name(cls) -> Text:
        return "airy"

    def __init__(self, system_token: Text, api_host: Text, last_message_id: Text, register_sent) -> None:
        self.system_token = system_token
        self.api_host = api_host
        self.last_message_id = last_message_id
        self.register_sent = register_sent

    async def send_response(self, recipient_id: Text, message: Dict[Text, Any]) -> None:
        logger.debug("send message %s", message)
        headers = {
            "Authorization": self.system_token
        }

        body = {
            "conversation_id": recipient_id,
            "message": {
                "text": message.get("text")
            }
        }
        res = requests.post("{}/messages.send".format(self.api_host), headers=headers, json=body)
        self.register_sent(message.get("text"))

        if not res.ok:
            logger.error(res.content)


class AiryInput(InputChannel):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Rasa Core and
    retrieve responses from the agent."""

    @classmethod
    def name(cls) -> Text:
        return "airy"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("system_token"),
            credentials.get("api_host"),
        )
        # pytype: enable=attribute-error

    def __init__(self, system_token: Text, api_host: Text) -> None:
        self.system_token = system_token
        self.api_host = api_host
        self.rasa_token = os.environ.get("RASA_TOKEN", None)
        self.sent_messages = []

    def register_sent(self, text: Text):
        self.sent_messages.append(text)

    def _is_user_message(self, req: Request) -> bool:
        # See https://airy.co/docs/core/api/webhook
        return req.json["payload"]["message"]["from_contact"] is False

    def _is_text_message(self, req: Request) -> bool:
        # See https://docs.airy.co/glossary#fields
        return req.json["type"] == "message.created" and "text" in req.json["payload"]["message"]["content"]

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        airy_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        # noinspection PyUnusedLocal
        @airy_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @airy_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            # Skip events that are not messages and messages
            # that are not sent from the source contact but from an Airy user
            logger.debug("received req %s", request.json)
            if not self._is_text_message(request):
                return response.text("success")

            conversation_id = request.json["payload"]["conversation_id"]
            text = request.json["payload"]["message"]["content"].get("text", None)

            if self._is_user_message(request):
                request.app.add_task(self.on_agent_uttered(request, conversation_id, text))
                return response.text("success")

            input_channel = self.name()
            metadata = self.get_metadata(request)

            airy_out = self._get_output_channel(request.json["payload"]["message"]["id"])
            # noinspection PyBroadException
            try:
                await on_new_message(
                    UserMessage(
                        text,
                        airy_out,
                        conversation_id,
                        input_channel=input_channel,
                        metadata=metadata,
                    )
                )
            except CancelledError:
                logger.error(
                    "Message handling timed out for "
                    "user message '{}'.".format(text)
                )
            except Exception:
                logger.exception(
                    "An exception occured while handling "
                    "user message '{}'.".format(text)
                )

            return response.text("success")

        return airy_webhook

    async def on_agent_uttered(self, request: Request, conversation_id: Text, text: Text):
        if text in self.sent_messages:
            return
        logger.debug("agent uttered on conv %s %s with token", conversation_id, text)
        app = request.app
        async with app.agent.lock_store.lock(conversation_id):
            processor = app.agent.create_processor()

            events = [BotUttered(text)]

            tracker = await update_conversation_with_events(
                conversation_id, processor, app.agent.domain, events
            )

            app.agent.tracker_store.save(tracker)

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        return {
            "source": request.json["payload"]["message"]["source"],
            "message_id": request.json["payload"]["message"]["id"]
        }

    def _get_output_channel(self, message_id) -> Optional["OutputChannel"]:
        return AiryBot(self.system_token, self.api_host, message_id, self.register_sent)
