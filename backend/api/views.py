from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from base.models import Event, EventRequest
from .serializers import EventSerializer, EventRequestSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404

@api_view(["GET"])
def getData(request):
	events = Event.objects.all()
	serializer = EventSerializer(events, many=True)
	return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addEvent(request):
	data = request.data.copy()
	data["organizer"] = request.user.id
	serializer = EventSerializer(data=data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def editEvent(request, event_id):
	try:
		event = Event.objects.get(pk=event_id)
	except Event.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	# Only organizer can edit/delete
	if event.organizer != request.user and request.method in ["PUT", "PATCH", "DELETE"]:
		return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

	if request.method == 'GET':
		serializer = EventSerializer(event, many=False)
		return Response(serializer.data)

	elif request.method == 'PUT':
		serializer = EventSerializer(event, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'PATCH':
		serializer = EventSerializer(event, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'DELETE':
		event.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
def signup(request):
	username = request.data.get("username")
	password = request.data.get("password")
	email = request.data.get("email", "")

	if not username or not password:
		return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

	if User.objects.filter(username=username).exists():
		return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

	user = User.objects.create_user(username=username, password=password, email=email)
	return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_event_api(request, event_id):
	"""Player requests to join an event (creates pending EventRequest)."""
	event = get_object_or_404(Event, pk=event_id)

	# Organizer cannot join their own event
	if event.organizer == request.user:
		return Response({"detail": "You are the organizer of this event."}, status=status.HTTP_400_BAD_REQUEST)

	# Check if already requested
	if EventRequest.objects.filter(event=event, user=request.user).exists():
		return Response({"detail": "You already requested to join this event."}, status=status.HTTP_400_BAD_REQUEST)

	# Check capacity
	if not event.has_space():
		return Response({"detail": "This event is full."}, status=status.HTTP_400_BAD_REQUEST)

	req = EventRequest.objects.create(event=event, user=request.user, status="pending")
	return Response(EventRequestSerializer(req).data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_requests_api(request, event_id):
	"""Organizer can see all join requests for their event."""
	event = get_object_or_404(Event, pk=event_id)

	if event.organizer != request.user:
		return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

	requests = event.requests.all()
	serializer = EventRequestSerializer(requests, many=True)
	return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_request_api(request, request_id):
	"""Organizer approves or rejects a join request."""
	join_request = get_object_or_404(EventRequest, pk=request_id)
	event = join_request.event

	if event.organizer != request.user:
		return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

	status_choice = request.data.get("status")
	if status_choice not in ["approved", "rejected"]:
		return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

	join_request.status = status_choice
	join_request.save()

	return Response(EventRequestSerializer(join_request).data)