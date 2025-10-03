from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path("", views.home, name='home'),
	path('<int:event_id>/', views.single, name='single'),
	path('event/<int:event_id>/join/', views.join_event, name="join_event"),
	path('signup/', views.signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name="login.html", next_page="home"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page="home"), name="logout"),
]