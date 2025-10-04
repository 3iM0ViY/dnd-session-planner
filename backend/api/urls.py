from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
	path("", views.getData),
	path("add/", views.addEvent),
	path('<int:event_id>/', views.editEvent, name='Event_detail'),

	# Auth
	path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("signup/", views.signup, name="signup"),

    # Event join/approval
    path("events/<int:event_id>/join/", views.join_event_api, name="api_join_event"),
    path("events/<int:event_id>/requests/", views.list_requests_api, name="api_list_requests"),
    path("requests/<int:request_id>/", views.update_request_api, name="api_update_request"),

    # Systems
    path("systems/", views.system_list_create, name="system_list_create"),
    path("systems/<int:system_id>/", views.system_detail, name="system_detail"),
]