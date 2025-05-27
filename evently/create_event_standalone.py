"""
Standalone script to add a simple event creation view to the Evently project.
This bypasses the existing URL configuration and view structure.
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evently.settings')
django.setup()

# Now we can import Django models
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.conf.urls import url
from django.conf import settings

from events.models import Event, Venue
from events.forms import EventForm

# Simple event creation view
@login_required
def simple_create_event(request):
    """Simplified event creation view"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            
            # Auto-generate slug if not provided
            if not event.slug:
                base_slug = slugify(event.title)
                slug = base_slug
                counter = 1
                while Event.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                event.slug = slug
            
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events')
        else:
            messages.error(request, 'There was an error creating the event. Please check the form.')
    else:
        form = EventForm()
    
    venues = Venue.objects.all()
    
    return render(request, 'events/simple_create_event.html', {
        'form': form,
        'venues': venues,
        'title': 'Create New Event'
    })

# Add this view to the URL patterns
def add_simple_create_event_url():
    """Add the simple create event URL to the project's URLs"""
    from django.urls import get_resolver
    from evently.urls import urlpatterns
    
    # Check if our URL is already in the patterns
    for pattern in urlpatterns:
        if hasattr(pattern, 'name') and pattern.name == 'simple_create_event':
            return
    
    # Add our URL pattern
    urlpatterns.append(
        path('simple-create-event/', simple_create_event, name='simple_create_event')
    )
    
    print("Simple create event URL added successfully!")

# Run this when the script is executed
if __name__ == "__main__":
    add_simple_create_event_url()
