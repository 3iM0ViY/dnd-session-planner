from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path("", views.home, name='home'),
	path('<int:event_id>/', views.single, name='single'),
	path('event/<int:event_id>/join/', views.join_event, name="join_event"),
	path('event/create/', views.create_event, name="create_event"),
	path('event/<int:event_id>/edit/', views.edit_event, name="edit_event"),
	path('event/<int:event_id>/delete/', views.delete_event, name="delete_event"),
	path('event/<int:event_id>/request/<int:request_id>/<str:action>/', views.manage_request, name="manage_request"),
	
	path('signup/', views.signup, name="signup"),
	path('login/', auth_views.LoginView.as_view(template_name="login.html", next_page="home"), name="login"),
	path('logout/', auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]