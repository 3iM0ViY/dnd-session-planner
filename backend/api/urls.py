from django.urls import path
from . import views

urlpatterns = [
	path("", views.getData),
	path("add/", views.addEvent),
	path('<int:event_id>/', views.editEvent, name='Event_detail'),
]