from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
	title = models.CharField(max_length=200, blank=True)
	game_setting = models.CharField(max_length=200, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	date_start = models.DateTimeField(blank=True, null=True)
	date_end = models.DateTimeField(blank=True, null=True)
	online = models.BooleanField(default=True)
	location = models.CharField(max_length=200, default="cafe/Discord server", blank=True, null=True)
	# organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
	created = models.DateTimeField(auto_now_add=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.title} ({self.date_start.date() if self.date_start else 'TBD'})"
