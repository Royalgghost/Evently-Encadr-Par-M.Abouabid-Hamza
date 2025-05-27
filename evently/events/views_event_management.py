from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
import uuid
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.http import HttpResponse

from .models import Event, EventRegistration, WaitingList, Venue, Notification
from .forms import EventForm, EventRegistrationForm, VenueForm

# Event Creation View - Function-based for simplicity and reliability
@login_required
def create_event(request):
    """Function-based view for event creation"""
    # Check permissions
    if not (request.user.is_superuser or request.user.is_staff):
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['admin', 'organizer']:
            messages.error(request, 'You do not have permission to create events.')
            return redirect('events')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
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
            
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', slug=event.slug)
        else:
            messages.error(request, 'There was an error creating the event. Please check the form and try again.')
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': 'Create Event',
        'venues': Venue.objects.all()
    }
    
    return render(request, 'events/event_form.html', context)

# Event Update View
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        # Notify registered participants about the update
        event = self.get_object()
        registrations = EventRegistration.objects.filter(event=event, status='confirmed')
        
        for registration in registrations:
            Notification.objects.create(
                user=registration.participant,
                title=f"Event Update: {event.title}",
                message=f"An event you have registered for has been updated. Please check the event details.",
                notification_type='update',
                event=event
            )
        
        messages.success(self.request, f'Event updated successfully! Registered participants have been notified.')
        return super().form_valid(form)
    
    def test_func(self):
        event = self.get_object()
        # Event organizer can always update their own events
        if self.request.user == event.organizer:
            return True
            
        # Allow superusers to update events
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
            
        # Check if user has a profile and is an admin
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'admin'
            
        # Default to False if no profile exists
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Event'
        return context

# Event Delete View
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events')
    
    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        # Notify registered participants about cancellation
        registrations = EventRegistration.objects.filter(event=event)
        
        for registration in registrations:
            Notification.objects.create(
                user=registration.participant,
                title=f"Event Cancelled: {event.title}",
                message=f"An event you registered for has been cancelled.",
                notification_type='cancellation',
                event=event
            )
        
        messages.success(self.request, f'Event cancelled successfully! Registered participants have been notified.')
        return super().delete(request, *args, **kwargs)
    
    def test_func(self):
        event = self.get_object()
        # Only event organizer or admins can delete events
        if self.request.user == event.organizer:
            return True
        if not hasattr(self.request.user, 'profile'):
            return False
        return self.request.user.profile.role == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Event'
        return context

# Venue Create View
class VenueCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Venue
    form_class = VenueForm
    template_name = 'events/venue_form.html'
    success_url = reverse_lazy('create_event')
    
    def test_func(self):
        # Allow superusers to create venues
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
            
        # Check if user has a profile and proper role
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['admin', 'organizer']
            
        # Default to False if no profile exists
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Venue'
        return context

# Venue Update View
class VenueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Venue
    form_class = VenueForm
    template_name = 'events/venue_form.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def test_func(self):
        # Allow superusers to update venues
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
            
        # Check if user has a profile and proper role
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['admin', 'organizer']
            
        # Default to False if no profile exists
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Venue'
        return context
        
# Venue Delete View
class VenueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Venue
    template_name = 'events/venue_confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def test_func(self):
        # Allow superusers to delete venues
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
            
        # Check if user has a profile and is an admin
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'admin'
            
        # Default to False if no profile exists
        return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Venue'
        return context

# Event Registration
@login_required
def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    # Check if registration is open
    if not event.is_registration_open():
        messages.error(request, "Registration for this event is closed.")
        return redirect('event_detail', slug=slug)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, participant=request.user).exists():
        messages.info(request, "You are already registered for this event.")
        return redirect('event_detail', slug=slug)
    
    # Check if user is on waiting list
    if WaitingList.objects.filter(event=event, user=request.user).exists():
        messages.info(request, "You are already on the waiting list for this event.")
        return redirect('event_detail', slug=slug)
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST, event=event, user=request.user)
        
        if form.is_valid():
            available_seats = event.available_seats()
            
            if available_seats > 0:
                # Create registration
                registration = EventRegistration(
                    event=event,
                    participant=request.user,
                    status='confirmed'
                )
                registration.save()
                
                # Create notification
                Notification.objects.create(
                    user=request.user,
                    title=f"Registration Confirmed: {event.title}",
                    message=f"You have successfully registered for {event.title}. The event starts on {event.start_date.strftime('%B %d, %Y at %I:%M %p')}.",
                    notification_type='registration',
                    event=event
                )
                
                messages.success(request, f"You have successfully registered for {event.title}!")
            else:
                # Add to waiting list
                waiting_list_count = WaitingList.objects.filter(event=event).count()
                waiting_list = WaitingList(
                    event=event,
                    user=request.user,
                    position=waiting_list_count + 1
                )
                waiting_list.save()
                
                # Create notification
                Notification.objects.create(
                    user=request.user,
                    title=f"Added to Waiting List: {event.title}",
                    message=f"The event is currently full. You have been added to the waiting list at position {waiting_list_count + 1}.",
                    notification_type='waiting_list',
                    event=event
                )
                
                messages.info(request, f"The event is full. You have been added to the waiting list.")
            
            return redirect('event_detail', slug=slug)
    else:
        form = EventRegistrationForm(event=event, user=request.user)
    
    return render(request, 'events/register_for_event.html', {
        'form': form,
        'event': event,
        'title': f'Register for {event.title}'
    })

# Cancel Registration
@login_required
def cancel_registration(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id, participant=request.user)
    event = registration.event
    
    if request.method == 'POST':
        # Delete registration
        registration.delete()
        
        # Check if there's anyone on the waiting list
        waiting_list = WaitingList.objects.filter(event=event).order_by('position').first()
        
        if waiting_list:
            # Move the first person from waiting list to registered
            new_registration = EventRegistration(
                event=event,
                participant=waiting_list.user,
                status='confirmed'
            )
            new_registration.save()
            
            # Create notification for the person moved from waiting list
            Notification.objects.create(
                user=waiting_list.user,
                title=f"Registration Confirmed: {event.title}",
                message=f"A spot has opened up and you've been moved from the waiting list. You are now registered for {event.title}.",
                notification_type='registration',
                event=event
            )
            
            # Delete from waiting list
            waiting_list.delete()
            
            # Update positions for remaining waiting list entries
            for i, entry in enumerate(WaitingList.objects.filter(event=event).order_by('position')):
                entry.position = i + 1
                entry.save()
        
        messages.success(request, f"Your registration for {event.title} has been cancelled.")
        return redirect('profile')
    
    return render(request, 'events/cancel_registration.html', {
        'registration': registration,
        'event': event,
        'title': 'Cancel Registration'
    })

# Generate Ticket PDF
@login_required
def generate_ticket(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id, participant=request.user)
    event = registration.event
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Draw the ticket content
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height-1*inch, "EVENT TICKET")
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-1.5*inch, event.title)
    
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, height-2*inch, f"Date: {event.start_date.strftime('%B %d, %Y')}")
    p.drawString(1*inch, height-2.2*inch, f"Time: {event.start_date.strftime('%I:%M %p')} - {event.end_date.strftime('%I:%M %p')}")
    
    if event.venue:
        p.drawString(1*inch, height-2.4*inch, f"Venue: {event.venue.name}")
        p.drawString(1*inch, height-2.6*inch, f"Address: {event.venue.address}, {event.venue.city}")
    elif event.location_address:
        p.drawString(1*inch, height-2.4*inch, f"Location: {event.location_address}")
    
    p.drawString(1*inch, height-3*inch, f"Attendee: {request.user.get_full_name() or request.user.username}")
    p.drawString(1*inch, height-3.2*inch, f"Ticket ID: {registration.unique_id}")
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(registration.unique_id))
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to a temporary file
    import tempfile
    import os
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    temp_file.close()
    
    # Draw the QR code using the file path
    p.drawImage(temp_file.name, width/2 - 1*inch, height-5*inch, width=2*inch, height=2*inch)
    
    # Schedule the temporary file for deletion after we're done with it
    # We'll delete it after the PDF is generated
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height-5.5*inch, "Please present this ticket at the event entrance")
    
    # Add footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, 0.5*inch, "Generated by Evently - Your Event Management Platform")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{registration.unique_id}.pdf"'
    
    # Clean up the temporary file
    os.unlink(temp_file.name)
    
    return response
