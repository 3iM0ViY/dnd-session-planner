from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import Event
from .serializers import EventSerializer

@api_view(["GET"])
def getData(request):
	events = Event.objects.all()
	serializer = EventSerializer(events, many=True)
	return Response(serializer.data)

@api_view(["POST"])
def addEvent(request):
	serializer = EventSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def editEvent(request, event_id):
	try:
		event = Event.objects.get(pk=event_id)
	except Event.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

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