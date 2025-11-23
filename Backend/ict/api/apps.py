from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ict.api"   # full Python path to the app
    label = "api"      # app label used in AUTH_USER_MODEL ("api.CustomUser")