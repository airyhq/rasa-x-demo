# -*- coding: utf-8 -*-
import logging
import pprint
import time
from typing import Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import (
    EventType, ConversationPaused
)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.airy_api import AiryApi
from actions.rasa_api import RasaApi

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)

MIN_SUGGESTION_CONF = 0.3


def get_event(intent: Text) -> Dict:
    return {
        "event": "user",
        "timestamp": time.time(),
        "metadata": {
            "is_external": True
        },
        "text": "EXTERNAL: " + intent,
        "parse_data": {
            "intent": {
                "name": intent
            },
            "text": "EXTERNAL: " + intent,
            "metadata": {
                "is_external": True
            }
        }
    }


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_suggest_replies"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[EventType]:
        current_state = tracker.current_state()

        # Top 3 intents with a confidence > MIN_SUGGESTION_CONF
        top_intents = [intent['name'] for intent in current_state['latest_message']['intent_ranking']
                       if intent['name'] != 'nlu_fallback' and intent['confidence'] > MIN_SUGGESTION_CONF][:3]
        logger.debug(f"top intents {','.join(top_intents)}")
        if len(top_intents) == 0:
            dispatcher.utter_message("Would you like to speak to a human?")
            return [ConversationPaused()]

        # Current event chain without last user message
        last_user_idx = 0
        for idx, event in reversed(list(enumerate(current_state['events']))):
            if 'event' in event and event['event'] == 'user':
                last_user_idx = idx
                break
        base_events = current_state['events'][:last_user_idx]

        rasa_api = RasaApi()
        airy_api = AiryApi()
        message_id = airy_api.get_last_message_id(current_state['sender_id'])
        if message_id is None:
            return []

        for intent in top_intents:
            pred_events = base_events + [get_event(intent)]

            top_action = rasa_api.predict_next_action(pred_events)
            logger.debug(top_action)
            if top_action is None or top_action not in domain['responses']:
                continue

            # Get a text response matching the action
            messages = [msg['text'] for msg in domain['responses'][top_action] if 'text' in msg]

            if len(messages) > 0:
                logger.debug(f"sending suggestions {','.join(messages)}")
                airy_api.suggest_replies(message_id, messages)

        return []
