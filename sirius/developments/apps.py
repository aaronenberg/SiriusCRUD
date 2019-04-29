from django.apps import AppConfig


class DevelopmentsConfig(AppConfig):
    name = 'developments'

    def ready(self):
        from . import signals
