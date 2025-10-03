from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventRequest
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
	events = Event.objects.all().select_related("organizer").prefetch_related("requests", "players").order_by("-date_start")
	data = []
	for event in events:
		request_status = None
		if request.user.is_authenticated:
			req = event.requests.filter(user=request.user).first()
			if req:
				request_status = req.status

		data.append({
			"event": event,
			"slots_taken": event.players.count(),
			"slots_total": event.max_players,
			"request_status": request_status,
		})
	return render(request, "index.html", {"events": data})

def single(request, event_id):
	event = Event.objects.get(pk=event_id)
	players = event.players.all()

	request_status = None
	if request.user.is_authenticated:
		req = event.requests.filter(user=request.user).first()
		if req:
			request_status = req.status

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
			'seconds': seconds,
			'players': players,
			'request_status': request_status,
		}
	else:
		data = {
			'event': None,
			'days': 0,
			'hours': 0,
			'minutes': 0,
			'seconds': 0,
			'players': [],
			'request_status': request_status,
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

@login_required
def join_event(request, event_id):
	event = get_object_or_404(Event, pk=event_id)

	# Organizer cannot join their own event
	if event.organizer == request.user:
		messages.error(request, "You are the organizer of this event.")
		return redirect("single", event_id=event_id)

	# Check if already requested
	existing = EventRequest.objects.filter(event=event, user=request.user).first()
	if existing:
		messages.info(request, "You already requested to join this event.")
		return redirect("single", event_id=event_id)

	# Check capacity
	if not event.has_space():
		messages.error(request, "This event is full.")
		return redirect("single", event_id=event_id)

	# Create a new pending request
	EventRequest.objects.create(event=event, user=request.user)
	messages.success(request, "Your request has been sent to the organizer.")
	return redirect("single", event_id=event_id)