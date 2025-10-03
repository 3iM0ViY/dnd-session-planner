from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Event(models.Model):
	title = models.CharField(max_length=200, blank=True)
	game_setting = models.CharField(max_length=200, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	date_start = models.DateTimeField(blank=True, null=True)
	date_end = models.DateTimeField(blank=True, null=True)
	online = models.BooleanField(default=True)
	location = models.CharField(max_length=200, default="cafe/Discord server", blank=True, null=True)
	max_players = models.PositiveSmallIntegerField(default=3, blank=True, null=True,)
	created = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	# DM who creates/organizes this event
	organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events", blank=True, null=True,)
	# Approved players — linked only after DM approves
	players = models.ManyToManyField(User, related_name="joined_events", through="EventRequest", blank=True, null=True,)

	def __str__(self):
		return f"{self.title} ({self.date_start.date() if self.date_start else 'TBD'})"

	def has_space(self):
		"""Check if the event still has room for new players."""
		return self.players.count() < self.max_players if self.max_players else True

class EventRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("event", "user")  # One request per user per event

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.status})"
