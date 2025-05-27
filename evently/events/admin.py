from django.contrib import admin
from .models import (
    UserProfile, Event, EventRegistration, 
    WaitingList, Venue, Notification
)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone_number')

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'capacity', 'organizer', 'is_published')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'description', 'location_address')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'

class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'participant', 'registration_date', 'status')
    list_filter = ('status', 'registration_date')
    search_fields = ('event__title', 'participant__username')
    date_hierarchy = 'registration_date'

class WaitingListAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'position', 'joined_date')
    list_filter = ('joined_date',)
    search_fields = ('event__title', 'user__username')

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'capacity')
    search_fields = ('name', 'address', 'city')
    list_filter = ('city',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'

# Register models
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(WaitingList, WaitingListAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Notification, NotificationAdmin)
