from django.contrib import admin
from .models import *

# Register your models here.
class EventAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "organizer", "system", "game_setting", "online", "max_players", "date_start", "updated_at", "created")
	list_display_links = ("title",)
	search_fields = ("title", "game_setting", "description", "location",)
	list_filter = ("system", "online",)
	readonly_fields = ("date_start", "updated_at", "created")

class SystemAdmin(admin.ModelAdmin):
	list_display = ("id", "name",)
	list_display_links = ("id",)
	list_editable = ("name",)

admin.site.register(Event, EventAdmin)
admin.site.register(System, SystemAdmin)