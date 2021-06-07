import json
import logging
from typing import Text, Dict, List, Any, Optional

import requests

from actions.config import rasa_host

logger = logging.getLogger(__name__)


class RasaApi:

    def __init__(self, host: Text = rasa_host):
        self.host = host

    def predict_next_action(self, events: List[Dict[Text, Any]]) -> Optional[Text]:
        endpoint = f"{self.host}/model/predict"

        response = requests.post(url=endpoint, json=events)
        if not response.ok:
            logger.error(response.content)
            return None

        scores = response.json()['scores']
        top_action = None
        top_score = 0

        for idx, score in enumerate(scores):
            if score['score'] > top_score:
                top_action = score['action']
                top_score = score['score']

        return top_action

