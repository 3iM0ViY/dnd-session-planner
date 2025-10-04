from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from base.models import Event, EventRequest, System
from .serializers import EventSerializer, EventRequestSerializer, SystemSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

@extend_schema(
	tags=["Events"],
	parameters=[
		OpenApiParameter(
			name='system',
			description='Filter events by the system name',
			required=False,
			type=str
		)
	],
	responses=EventSerializer(many=True),
	summary="Get Events"
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def getData(request):
	"""Receive all Events, ordered by how soon their date_start is"""
	events = Event.objects.all()

	# Filtering by system name
	system_name = request.GET.get("system")
	if system_name:
		events = events.filter(system__name__iexact=system_name)

	serializer = EventSerializer(events, many=True)
	return Response(serializer.data)

@extend_schema(
    tags=["Events"],
    operation_id="createEvent",
    summary="Create an event",
    description=(
        "Create a new event. The organizer is automatically set from the authenticated user "
        "(request.user) and is read-only. The `players` list is read-only and will be empty "
        "on creation. For `system`, provide the system name (slug_field='name'). "
        "Dates must be ISO 8601 strings. If `online` is true, `location` can describe the "
        "virtual venue (e.g., a Discord server)."
    ),
    request=EventSerializer,
    responses={
        201: OpenApiResponse(
            response=EventSerializer,
            description="Event successfully created."
        ),
        400: OpenApiResponse(
            description="Validation error. The response contains field-specific error details."
        ),
    },
    examples=[
        OpenApiExample(
            name="Create Avatar Legends event (request)",
            value={
                "title": "Rocky Road from Ba-Sing-Se",
                "system": "Avatar Legends: The Roleplaying Game",
                "game_setting": "The Earth kingdoms",
                "description": (
                    "A group of benders gets into a diplomatic affair accompanying an "
                    "ambassador from the Fire Nation."
                ),
                "date_start": "2025-10-06T19:30:00Z",
                "date_end": "2025-10-06T21:30:00Z",
                "online": True,
                "location": "Deathbringer discord server",
                "max_players": 6
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Event created (201 response)",
            value={
                "id": 17,
                "organizer": "yul",
                "players": [],
                "system": "Avatar Legends: The Roleplaying Game",
                "title": "Rocky Road from Ba-Sing-Se",
                "game_setting": "The Earth kingdoms",
                "description": (
                    "A group of benders gets into a diplomatic affair accompanying an "
                    "ambassador from the Fire Nation."
                ),
                "date_start": "2025-10-06T22:30:00+03:00",
                "date_end": "2025-10-07T00:30:00+03:00",
                "online": True,
                "location": "Deathbringer discord server",
                "max_players": 6,
                "created": "2025-10-04T17:18:26.562903+03:00",
                "updated_at": "2025-10-04T17:18:26.562903+03:00"
            },
            response_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addEvent(request):
	serializer = EventSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save(organizer=request.user) #fix: organizer is added here
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
	tags=["Events"],
    description='Retrieve a single event by ID.',
    methods=["GET"],
    responses={
        200: EventSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided or given token not valid for any token type",
            examples=[{"detail": "token_not_valid"}]
        ),
        403: OpenApiResponse(
            description="Not authorized.",
            examples=[{"detail": "Not authorized."}]
        ),
        404: OpenApiResponse(
            description="Event not found.",
            examples=[{"detail": "Not found."}]
        )
    },
    summary="Get event by id"
)
@extend_schema(
	tags=["Events"],
    description='Replace an existing event. Only organizer can update.',
    methods=["PUT"],
    responses={
        200: EventSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided or given token not valid for any token type",
            examples=[{"detail": "token_not_valid"}]
        ),
        403: OpenApiResponse(
            description="Not authorized.",
            examples=[{"detail": "Not authorized."}]
        ),
        404: OpenApiResponse(
            description="Event not found.",
            examples=[{"detail": "Not found."}]
        )
    },
    summary="Replace an event info"
)
@extend_schema(
	tags=["Events"],
    description='Partially update an event. Only organizer can update.',
    methods=["PATCH"],
    responses={
        200: EventSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided or given token not valid for any token type",
            examples=[{"detail": "token_not_valid"}]
        ),
        403: OpenApiResponse(
            description="Not authorized.",
            examples=[{"detail": "Not authorized."}]
        ),
        404: OpenApiResponse(
            description="Event not found.",
            examples=[{"detail": "Not found."}]
        )
    },
    summary="Edit an event"
)
@extend_schema(
	tags=["Events"],
    description='Delete an event. Only organizer can delete.',
    methods=["DELETE"],
    responses={
        204: OpenApiResponse(
            description="Deleted successfully.",
            examples=[{"detail": "Deleted successfully."}]
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or given token not valid for any token type",
            examples=[{"detail": "token_not_valid"}]
        ),
        403: OpenApiResponse(
            description="Not authorized.",
            examples=[{"detail": "Not authorized."}]
        ),
        404: OpenApiResponse(
            description="Event not found.",
            examples=[{"detail": "Not found."}]
        )
    },
    summary="Delete an event"
)
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
		return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

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

@api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated])
def system_list_create(request):
	"""List all systems or create a new one."""
	if request.method == "GET":
		systems = System.objects.all()
		serializer = SystemSerializer(systems, many=True)
		return Response(serializer.data)

	elif request.method == "POST":
		serializer = SystemSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def system_detail(request, system_id):
	"""Retrieve, update, or delete a single system."""
	try:
		system = System.objects.get(pk=system_id)
	except System.DoesNotExist:
		return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

	if request.method == "GET":
		serializer = SystemSerializer(system)
		return Response(serializer.data)

	elif request.method in ["PUT", "PATCH"]:
		serializer = SystemSerializer(system, data=request.data, partial=(request.method == "PATCH"))
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == "DELETE":
		system.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)