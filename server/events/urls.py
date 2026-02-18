from django.urls import path
from . import views

urlpatterns = [
    path('event', views.send_event, name='send_event'),
    path('event-log', views.get_event_log, name='event_log'),
]
