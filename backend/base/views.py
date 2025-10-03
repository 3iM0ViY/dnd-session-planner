from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.utils import timezone
from .models import Event
from .forms import SignUpForm

# Create your views here.

def home(request):
	events = Event.objects.all().order_by("-date_start")
	return render(request, "index.html", {"events": events})

def single(request, event_id):
	event = Event.objects.get(pk=event_id)
	if event and event.date_start:
		time_remaining = event.date_start - timezone.now()
		days = time_remaining.days
		hours = (time_remaining.seconds // 3600)
		minutes = (time_remaining.seconds % 3600) // 60
		seconds = time_remaining.seconds % 60
		data = {
			'event': event,
			'days': days,
			'hours': hours,
			'minutes': minutes,
			'seconds': seconds
		}
	else:
		data = {
			'event': None,
			'days': 0,
			'hours': 0,
			'minutes': 0,
			'seconds': 0
		}
	return render(request, 'single.html', {'data': data})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})