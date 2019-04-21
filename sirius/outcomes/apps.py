from django.apps import AppConfig


class OutcomesConfig(AppConfig):
    name = 'outcomes'

    def ready(self):
        from . import signals
