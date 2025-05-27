from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.urls import reverse

# Define User Roles
ROLE_CHOICES = (
    ('admin', 'Administrator'),
    ('organizer', 'Organizer'),
    ('participant', 'Participant'),
)

# Define Event Categories
EVENT_CATEGORIES = (
    ('conference', 'Conference'),
    ('workshop', 'Workshop'),
    ('meetup', 'Meetup'),
    ('seminar', 'Seminar'),
    ('other', 'Other'),
)

class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Venue(models.Model):
    """Model for event venues"""
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    """Model for events"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES, default='other')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name='events')
    location_address = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    poster_image = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    is_published = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
    def clean(self):
        # Validate event dates
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")
        
        if self.registration_deadline and self.registration_deadline > self.start_date:
            raise ValidationError("Registration deadline must be before event start date")
    
    def is_registration_open(self):
        now = timezone.now()
        if self.registration_deadline:
            return now <= self.registration_deadline
        return now <= self.start_date
    
    def available_seats(self):
        registered_count = self.registrations.filter(status='confirmed').count()
        return max(0, self.capacity - registered_count)
    
    def is_past_event(self):
        return timezone.now() > self.end_date

class EventRegistration(models.Model):
    """Model for event registrations"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['event', 'participant']
    
    def __str__(self):
        return f"{self.participant.username} - {self.event.title}"

class WaitingList(models.Model):
    """Model for event waiting list entries"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='waiting_list')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waiting_lists')
    joined_date = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['joined_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = (
        ('registration', 'Registration Confirmation'),
        ('reminder', 'Event Reminder'),
        ('cancellation', 'Event Cancellation'),
        ('update', 'Event Update'),
        ('waiting_list', 'Waiting List Update'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

class ImageLibrary(models.Model):
    """Model for storing images in the admin image library"""
    IMAGE_CATEGORIES = (
        ('event', 'Event'),
        ('venue', 'Venue'),
        ('banner', 'Banner'),
        ('profile', 'Profile'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='image_library/')
    category = models.CharField(max_length=20, choices=IMAGE_CATEGORIES, default='other')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Image Library'
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
