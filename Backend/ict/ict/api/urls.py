from django.urls import path, include
from .views import *

urlpatterns = [
    path('test/', test, name='test'),
    path('get_data/', get_data, name='get_data')
]
    