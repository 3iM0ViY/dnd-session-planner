from rest_framework import serializers
from base.models import Event, EventRequest

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.ReadOnlyField(source="organizer.username")
    players = serializers.StringRelatedField(many=True, read_only=True)
    system = serializers.ReadOnlyField(source="system.name")

    class Meta:
        model = Event
        fields = "__all__"


class EventRequestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    event = serializers.ReadOnlyField(source="event.id")

    class Meta:
        model = EventRequest
        fields = ["id", "event", "user", "status", "created_at"]
