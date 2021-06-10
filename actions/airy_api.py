import logging
import logging
import time
import uuid
from typing import Text, List, Optional

import requests

from actions.config import airy_host, airy_token

logger = logging.getLogger(__name__)


class AiryApi:

    def __init__(self, host: Text = airy_host, system_token: Text = airy_token):
        self.host = host
        self.system_token = system_token

    def suggest_replies(self, message_id: Text, messages: List[Text]):
        suggestions = {}
        for message in messages:
            suggestions[str(uuid.uuid5(uuid.UUID(message_id), message))] = {
                'content': {
                    'text': message
                }
            }

        response = requests.post(url=f"{self.host}/messages.suggestReplies", json={
            'message_id': message_id,
            'suggestions': suggestions
        })
        if not response.ok:
            logger.error(response.content)

    def get_last_message_id(self, conversation_id: Text, retries: int = 3) -> Optional[Text]:
        response = requests.post(url=f"{self.host}/messages.list", json={
            'conversation_id': conversation_id
        })
        if not response.ok:
            if retries < 1:
                logger.error(response.content)
                return None
            else:
                # Retry so that streaming endpoints can catch up
                time.sleep(.5)
                return self.get_last_message_id(conversation_id, retries - 1)

        messages = response.json()
        for message in messages['data']:
            if message["from_contact"] is True:
                return message["id"]
        else:
            logger.error("No user message found in conversation %s", conversation_id)
            return None
