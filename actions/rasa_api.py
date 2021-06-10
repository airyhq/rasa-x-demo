import json
import logging
from typing import Text, Dict, List, Any, Optional

import requests

from actions.config import rasa_host, rasa_token

logger = logging.getLogger(__name__)


class RasaApi:

    def __init__(self, host: Text = rasa_host, token: Text = rasa_token):
        self.host = host
        self.token = token

    def predict_next_action(self, events: List[Dict[Text, Any]]) -> Optional[Text]:
        endpoint = f"{self.host}/model/predict"

        params = {}
        if self.token is not None:
            params['token'] = self.token

        response = requests.post(url=endpoint, json=events, params=params)
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

