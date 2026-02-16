from django.apps import AppConfig

import os

class CoreConfig(AppConfig):
    name = "core"
    
    address = "127.0.0.1:8000"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        print("Repwatch server up (lifecycle entrypoint)")
