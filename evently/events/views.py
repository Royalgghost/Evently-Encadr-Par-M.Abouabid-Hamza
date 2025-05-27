from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q, Count

from .models import Event, UserProfile, EventRegistration, WaitingList, Venue, Notification
from .forms import (
    UserRegisterForm, UserProfileForm, UserUpdateForm, EventForm, 
    EventRegistrationForm, EventFilterForm, VenueForm
)

# Home Page View
def home(request):
    upcoming_events = Event.objects.filter(
        is_published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    
    return render(request, 'events/home.html', {
        'upcoming_events': upcoming_events,
        'title': 'Home'
    })

# User Registration
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user first - this will trigger the signal to create a profile
            user = user_form.save()
            
            # Now update the existing profile with form data instead of creating a new one
            profile = user.profile  # Get the profile created by the signal
            
            # Update profile with form data
            profile.bio = profile_form.cleaned_data.get('bio', '')
            profile.phone_number = profile_form.cleaned_data.get('phone_number', '')
            
            # Handle profile picture if provided
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                
            profile.save()
            
            # Auto-login after registration
            login(request, user)
            messages.success(request, f'Your account has been created! You are now logged in.')
            return redirect('home')
    else:
        user_form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    return render(request, 'events/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Register'
    })

# User Profile View
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    # Get user's event registrations
    user_registrations = EventRegistration.objects.filter(
        participant=request.user,
        event__start_date__gte=timezone.now()
    ).order_by('event__start_date')
    
    # Get user's organized events if they are an organizer
    organized_events = None
    if hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'organizer']:
        organized_events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    return render(request, 'events/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_registrations': user_registrations,
        'organized_events': organized_events,
        'notifications': notifications,
        'title': 'Profile'
    })

# Events List View
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_published=True).order_by('start_date')
        
        # Apply filters if provided
        filter_form = EventFilterForm(self.request.GET)
        if filter_form.is_valid():
            filter_by = filter_form.cleaned_data.get('filter_by')
            category = filter_form.cleaned_data.get('category')
            date_from = filter_form.cleaned_data.get('date_from')
            date_to = filter_form.cleaned_data.get('date_to')
            search = filter_form.cleaned_data.get('search')
            
            if filter_by == 'upcoming':
                queryset = queryset.filter(start_date__gte=timezone.now())
            elif filter_by == 'past':
                queryset = queryset.filter(start_date__lt=timezone.now())
            
            if category:
                queryset = queryset.filter(category=category)
            
            if date_from:
                queryset = queryset.filter(start_date__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(start_date__date__lte=date_to)
            
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(description__icontains=search) |
                    Q(location_address__icontains=search)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EventFilterForm(self.request.GET)
        context['title'] = 'Events'
        return context

# Event Detail View
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if user is registered
        is_registered = False
        is_on_waitlist = False
        registration = None
        
        if self.request.user.is_authenticated:
            # Check if user is registered for this event
            registration = EventRegistration.objects.filter(
                event=event, 
                participant=self.request.user
            ).first()
            
            is_registered = registration is not None
            
            # Check if user is on waiting list
            is_on_waitlist = WaitingList.objects.filter(
                event=event,
                user=self.request.user
            ).exists()
        
        context['is_registered'] = is_registered
        context['is_on_waitlist'] = is_on_waitlist
        context['registration'] = registration
        context['registration_form'] = EventRegistrationForm(event=event, user=self.request.user)
        context['available_seats'] = event.available_seats()
        context['is_registration_open'] = event.is_registration_open()
        context['title'] = event.title
        
        return context
