from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import Event
from .serializers import EventSerializer

@api_view(["GET"])
def getData(request):
	events = Event.objects.all()
	serializer = EventSerializer(events, many=True)
	return Response(serializer.data)