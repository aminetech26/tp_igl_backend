from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Articles'
    
    def ready(self):
        import Articles.signals # noqa