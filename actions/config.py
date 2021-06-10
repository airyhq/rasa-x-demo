# -*- coding: utf-8 -*-
import os

rasa_host = os.environ.get("RASA_HOST", "http://localhost:5005")
rasa_token = os.environ.get("RASA_TOKEN", None)

airy_host = os.environ.get("AIRY_HOST", "http://airy.core")
airy_token = os.environ.get("SYSTEM_TOKEN", None)
