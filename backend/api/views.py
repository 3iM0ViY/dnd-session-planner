from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from base.models import Event, EventRequest, System
from .serializers import EventSerializer, EventRequestSerializer, SystemSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

param_event_id = OpenApiParameter(
	name="event_id",
	type=int,
	location=OpenApiParameter.PATH,
	description="The unique ID of the event."
)

@extend_schema(
	tags=["Events"],
	operation_id="listEvents",
	summary="Get Events",
	description=(
		"Retrieve a list of all events, ordered by how soon their `date_start` is. "
		"Optionally, filter events by TTRPG system using the `system` query parameter. "
		"If no filter is applied, all events are returned."
	),
	parameters=[
		OpenApiParameter(
			name='system',
			description='Filter events by the system name (case-insensitive). Will return an empty list if there is match with any of the `system.name`s.',
			required=False,
			type=str,
			examples=[
				OpenApiExample(
					name="Example parameter",
					value="/?system=Cyberpunk RED",
					response_only=True
				)
			]
		)
	],
	responses=OpenApiResponse(
		response=EventSerializer(many=True),
		description="List of events matching the filter (or all events if no filter)."
	),
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
		"on creation. For `system`, provide the system name `(slug_field='name')`. "
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

@extend_schema_view(
	get=extend_schema(
		tags=["Events"],
		summary="Get event by id",
		description="Retrieve a single event by ID.",
		parameters=[param_event_id],
		responses={
			200: EventSerializer,
			401: OpenApiResponse(
				description="Authentication credentials were not provided or token invalid.",
				examples=[
					OpenApiExample(
						"Unauthorized",
						value={"detail": "token_not_valid"},
						response_only=True,
					)
				],
			),
			403: OpenApiResponse(
				description="Not authorized.",
				examples=[OpenApiExample("Forbidden", value={"detail": "Not authorized."}, response_only=True)],
			),
			404: OpenApiResponse(
				description="Event not found.",
				examples=[OpenApiExample("NotFound", value={"detail": "Not found."}, response_only=True)],
			),
		},
		examples=[
			OpenApiExample(
				"Event details (200)",
				value={
					"id": 5,
					"organizer": "yul",
					"players": ["yulik", "yulian"],
					"system": None,
					"title": "Curse of the Whispering Woods",
					"game_setting": "Whispering Woods",
					"description": "Explore a haunted forest and break a deadly curse.",
					"date_start": "2025-11-01T12:00:00+02:00",
					"date_end": "2025-11-01T17:00:00+02:00",
					"online": True,
					"location": "Kyiv, downtown",
					"max_players": 3,
					"created": "2025-10-02T18:26:03.059575+03:00",
					"updated_at": "2025-10-03T18:25:17.113148+03:00",
				},
				response_only=True,
			)
		],
		operation_id="getEventById",
	),
	put=extend_schema(
		tags=["Events"],
		summary="Replace an event info",
		description="Replace an existing event. Only the organizer can update.",
		parameters=[param_event_id],
		request=EventSerializer,
		responses={
			200: EventSerializer,
			401: OpenApiResponse(
				description="Authentication credentials were not provided or token invalid.",
				examples=[OpenApiExample("Unauthorized", value={"detail": "token_not_valid"}, response_only=True)],
			),
			403: OpenApiResponse(
				description="Not authorized.",
				examples=[OpenApiExample("Forbidden", value={"detail": "Not authorized."}, response_only=True)],
			),
			404: OpenApiResponse(
				description="Event not found.",
				examples=[OpenApiExample("NotFound", value={"detail": "Not found."}, response_only=True)],
			),
			400: OpenApiResponse(
				description="Validation error.",
				examples=[OpenApiExample("BadRequest", value={"title": ["This field is required."]}, response_only=True)],
			),
		},
		examples=[
			OpenApiExample(
				"Replace (request)",
				value={
					"title": "Curse of the Whispering Woods - Revised",
					"system": "DnD5e",
					"game_setting": "Whispering Woods",
					"description": "Updated description",
					"date_start": "2025-11-01T12:00:00Z",
					"date_end": "2025-11-01T17:00:00Z",
					"online": True,
					"location": "Kyiv, downtown",
					"max_players": 4,
				},
				request_only=True,
			),
			OpenApiExample(
				"Replace (200 response)",
				value={
					"id": 5,
					"organizer": "yul",
					"players": ["yulik", "yulian"],
					"system": "DnD5e",
					"title": "Curse of the Whispering Woods - Revised",
					"game_setting": "Whispering Woods",
					"description": "Updated description",
					"date_start": "2025-11-01T12:00:00+00:00",
					"date_end": "2025-11-01T17:00:00+00:00",
					"online": True,
					"location": "Kyiv, downtown",
					"max_players": 4,
					"created": "2025-10-02T18:26:03.059575+03:00",
					"updated_at": "2025-10-04T10:00:00+03:00",
				},
				response_only=True,
			),
		],
		operation_id="replaceEventById",
	),
	patch=extend_schema(
		tags=["Events"],
		summary="Edit an event",
		description="Partially update an event. Only the organizer can update.",
		parameters=[param_event_id],
		request=EventSerializer,
		responses={
			200: EventSerializer,
			401: OpenApiResponse(
				description="Authentication credentials were not provided or token invalid.",
				examples=[OpenApiExample("Unauthorized", value={"detail": "token_not_valid"}, response_only=True)],
			),
			403: OpenApiResponse(
				description="Not authorized.",
				examples=[OpenApiExample("Forbidden", value={"detail": "Not authorized."}, response_only=True)],
			),
			404: OpenApiResponse(
				description="Event not found.",
				examples=[OpenApiExample("NotFound", value={"detail": "Not found."}, response_only=True)],
			),
			400: OpenApiResponse(
				description="Validation error.",
				examples=[OpenApiExample("BadRequest", value={"max_players": ["Ensure this value is less than or equal to 100."]}, response_only=True)],
			),
		},
		examples=[
			OpenApiExample(
				"Partial update (request)",
				value={"title": "Curse of the Whispering Woods — Final"},
				request_only=True,
			),
			OpenApiExample(
				"Partial update (200 response)",
				value={
					"id": 5,
					"organizer": "yul",
					"players": ["yulik", "yulian"],
					"system": None,
					"title": "Curse of the Whispering Woods — Final",
					"game_setting": "Whispering Woods",
					"description": "Explore a haunted forest and break a deadly curse.",
					"date_start": "2025-11-01T12:00:00+02:00",
					"date_end": "2025-11-01T17:00:00+02:00",
					"online": True,
					"location": "Kyiv, downtown",
					"max_players": 3,
					"created": "2025-10-02T18:26:03.059575+03:00",
					"updated_at": "2025-10-04T11:20:00+03:00",
				},
				response_only=True,
			),
		],
		operation_id="partialUpdateEventById",
	),
	delete=extend_schema(
		tags=["Events"],
		summary="Delete an event",
		description="Delete an event. Only the organizer can delete.",
		parameters=[param_event_id],
		responses={
			204: OpenApiResponse(
				description="Deleted successfully.",
				examples=[OpenApiExample("NoContent", value={"detail": "Deleted successfully."}, response_only=True)],
			),
			401: OpenApiResponse(
				description="Authentication credentials were not provided or token invalid.",
				examples=[OpenApiExample("Unauthorized", value={"detail": "token_not_valid"}, response_only=True)],
			),
			403: OpenApiResponse(
				description="Not authorized.",
				examples=[OpenApiExample("Forbidden", value={"detail": "Not authorized."}, response_only=True)],
			),
			404: OpenApiResponse(
				description="Event not found.",
				examples=[OpenApiExample("NotFound", value={"detail": "Not found."}, response_only=True)],
			),
		},
		operation_id="deleteEventById",
	),
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

@extend_schema(
    tags=["Authentication"],
    operation_id="userSignup",
    summary="Register a new user",
    description=(
        "Create a new user account by providing a unique username and password. "
        "Email is optional. If the username already exists, an error is returned."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "example": "new_player"},
                "password": {"type": "string", "example": "secret123"},
                "email": {"type": "string", "example": "new_player@example.com"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        201: OpenApiResponse(
            response={"application/json": {"example": {"message": "User created successfully"}}},
            description="User successfully registered."
        ),
        400: OpenApiResponse(
            response={"application/json": {"example": {"error": "Username already taken"}}},
            description="Invalid input or username already taken."
        ),
    },
)
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

@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        operation_id="obtainTokenPair",
        summary="Obtain JWT access and refresh tokens",
        description=(
            "Authenticate a user and obtain an access and refresh token pair. "
            "The access token is used for authenticated API requests, "
            "while the refresh token can be exchanged for a new access token."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "yul"},
                    "password": {"type": "string", "example": "secret123"},
                },
                "required": ["username", "password"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsInR5..."},
                    "access": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsInR5..."},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "No active account found with the given credentials"}
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Valid login",
                value={"refresh": "<refresh_token>", "access": "<access_token>"},
                response_only=True,
            ),
        ],
    )
)
class TokenObtainPairViewSchema(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        operation_id="refreshToken",
        summary="Refresh the access token",
        description=(
            "Exchange a valid refresh token for a new access token. "
            "Use this endpoint when your access token has expired."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "example": "<refresh_token>"},
                },
                "required": ["refresh"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "example": "<new_access_token>"},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "Token is invalid or expired"},
                },
            },
        },
    )
)
class TokenRefreshViewSchema(TokenRefreshView):
    pass

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