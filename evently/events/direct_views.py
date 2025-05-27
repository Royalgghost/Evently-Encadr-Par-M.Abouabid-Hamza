from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone

from .models import Event, Venue
from .forms import EventForm

@login_required
def direct_create_event(request):
    """
    Direct function-based view for event creation
    """
    # Get all venues for the form
    venues = Venue.objects.all()
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            try:
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
                return redirect('events')
            except Exception as e:
                messages.error(request, f'Error saving event: {str(e)}')
        else:
            # Display a general error message
            messages.error(request, 'There was an error creating the event. Please check the form below for details.')
            
            # Also display detailed form errors
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = field.replace('_', ' ').title()
                    messages.error(request, f'{field_name}: {error}')
    else:
        # GET request - display empty form
        form = EventForm()
    
    # Calculate statistics for context
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(start_date__gte=timezone.now()).count()
    
    context = {
        'form': form,
        'venues': venues,
        'title': 'Create New Event',
        'total_events': total_events,
        'upcoming_events': upcoming_events_count
    }
    
    return render(request, 'events/direct_create_event.html', context)
