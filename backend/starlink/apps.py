from django.apps import AppConfig


class StarlinkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'starlink'

    def ready(self):
        import starlink.signals  # noqa
