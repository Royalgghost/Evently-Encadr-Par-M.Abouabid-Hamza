"""
URL configuration for evently project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils import timezone

# Import the simple event creation view
from events.models import Event, Venue
from events.forms import EventForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

@login_required
def simple_create_event(request):
    """Simplified event creation view with detailed error handling"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            try:
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
                
                # Save the event
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
        # Initialize form with default values for required fields
        initial_data = {
            'start_date': timezone.now() + timezone.timedelta(days=1),
            'end_date': timezone.now() + timezone.timedelta(days=1, hours=2),
            'capacity': 50,
            'is_published': True
        }
        form = EventForm(initial=initial_data)
    
    venues = Venue.objects.all()
    
    return render(request, 'events/simple_create_event.html', {
        'form': form,
        'venues': venues,
        'title': 'Create New Event',
        'form_errors': form.errors if request.method == 'POST' else None
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    
    # Add simple event creation view directly in the main URLs
    path('simple-create-event/', simple_create_event, name='simple_create_event'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
