from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event


class SignUpForm(UserCreationForm):
	email = forms.EmailField(
		required=True,
		help_text="Required. Enter a valid email address."
	)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)
		# Add Bootstrap styling
		for field_name, field in self.fields.items():
			field.widget.attrs['class'] = 'form-control'

# Event Registration
class EventForm(forms.ModelForm):
	class Meta:
		model = Event
		fields = [
			"title", "system", "game_setting", "description",
			"date_start", "date_end", "online", "location", "max_players"
		]
		widgets = {
			"date_start": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
			"date_end": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs["class"] = "form-control"