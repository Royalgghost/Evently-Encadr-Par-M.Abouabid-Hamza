from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

from .models import Event, Venue
from .forms import EventForm

@login_required
def create_event_view(request):
    """
    Simple function-based view for event creation
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to create an event.')
        return redirect('login')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            # Create event but don't save to DB yet
            event = form.save(commit=False)
            
            # Set the organizer to the current user
            event.organizer = request.user
            
            # Auto-generate slug if not provided
            if not event.slug:
                base_slug = slugify(event.title)
                # Check if slug already exists and make it unique if needed
                slug = base_slug
                counter = 1
                while Event.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                event.slug = slug
            
            # Save the event to the database
            event.save()
            
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', slug=event.slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # GET request - display empty form
        form = EventForm()
    
    # Get all venues for the form
    venues = Venue.objects.all()
    
    return render(request, 'events/create_event.html', {
        'form': form,
        'venues': venues,
        'title': 'Create New Event'
    })
