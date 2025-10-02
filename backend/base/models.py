from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    location = models.CharField(max_length=200)
    # organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.date_start.date()})"
