# -*- coding: utf-8 -*-
import os

rasa_host = os.environ.get("RASA_HOST", "http://localhost:5005")

airy_host = os.environ.get("AIRY_HOST", "http://airy.core")
airy_token = os.environ.get("SYSTEM_TOKEN", None)
