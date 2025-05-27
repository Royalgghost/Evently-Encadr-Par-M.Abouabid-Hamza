from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from .models import Event, UserProfile, Venue, EventRegistration, WaitingList, Notification, ImageLibrary
from .forms import ImageLibraryForm

def is_admin_or_organizer(user):
    """Check if user is admin or organizer"""
    # More permissive check that also allows superusers
    if user.is_authenticated:
        if user.is_superuser or user.is_staff:
            return True
        if hasattr(user, 'profile'):
            # Check if role contains 'admin' or 'organizer' as substring
            return 'admin' in user.profile.role or 'organizer' in user.profile.role
    return False

@login_required
@user_passes_test(is_admin_or_organizer)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get today's date for event status
    today = timezone.now().date().isoformat()
    now = timezone.now()
    
    # Get filter parameters
    event_filter = request.GET.get('event_filter', 'all')
    user_filter = request.GET.get('user_filter', 'all')
    
    # Get events with filtering
    if event_filter == 'upcoming':
        events = Event.objects.filter(start_date__gte=now).order_by('start_date')
    elif event_filter == 'past':
        events = Event.objects.filter(end_date__lt=now).order_by('-end_date')
    elif event_filter == 'today':
        events = Event.objects.filter(start_date__date=now.date()).order_by('start_date')
    elif event_filter == 'published':
        events = Event.objects.filter(is_published=True).order_by('-start_date')
    elif event_filter == 'draft':
        events = Event.objects.filter(is_published=False).order_by('-start_date')
    else:  # 'all'
        events = Event.objects.all().order_by('-start_date')
    
    # Get user profiles with filtering
    if user_filter == 'admin':
        users = UserProfile.objects.filter(role='admin').select_related('user')
    elif user_filter == 'organizer':
        users = UserProfile.objects.filter(role='organizer').select_related('user')
    elif user_filter == 'participant':
        users = UserProfile.objects.filter(role='participant').select_related('user')
    else:  # 'all'
        users = UserProfile.objects.all().select_related('user')
    
    # Get venues
    venues = Venue.objects.all()
    
    # Get images
    images = ImageLibrary.objects.all().order_by('-upload_date')[:20]  # Limit to recent 20
    
    # Get recent registrations
    recent_registrations = EventRegistration.objects.select_related('event', 'participant').order_by('-registration_date')[:10]
    
    # Calculate statistics
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(start_date__gte=now).count()
    past_events_count = Event.objects.filter(end_date__lt=now).count()
    
    total_users = UserProfile.objects.count()
    organizer_count = UserProfile.objects.filter(role='organizer').count()
    attendee_count = UserProfile.objects.filter(role='participant').count()
    
    total_registrations = EventRegistration.objects.count()
    confirmed_registrations = EventRegistration.objects.filter(status='confirmed').count()
    waitlist_registrations = WaitingList.objects.count()
    
    conference_count = Event.objects.filter(category='conference').count()
    workshop_count = Event.objects.filter(category='workshop').count()
    social_count = Event.objects.filter(category='meetup').count()
    seminar_count = Event.objects.filter(category='seminar').count()
    
    # Get events with low capacity remaining
    from django.db.models import F, ExpressionWrapper, IntegerField, Count
    events_with_registrations = Event.objects.filter(start_date__gte=now).annotate(
        registration_count=Count('registrations', filter=Q(registrations__status='confirmed'))
    ).annotate(
        remaining_capacity=ExpressionWrapper(F('capacity') - F('registration_count'), output_field=IntegerField())
    ).filter(remaining_capacity__lt=10).order_by('remaining_capacity', 'start_date')[:5]
    
    context = {
        'events': events,
        'users': users,
        'venues': venues,
        'images': images,
        'today': today,
        'event_filter': event_filter,
        'user_filter': user_filter,
        'recent_registrations': recent_registrations,
        'events_with_low_capacity': events_with_registrations,
        'total_events': total_events,
        'upcoming_events_count': upcoming_events_count,
        'past_events_count': past_events_count,
        'total_users': total_users,
        'organizer_count': organizer_count,
        'attendee_count': attendee_count,
        'total_registrations': total_registrations,
        'confirmed_registrations': confirmed_registrations,
        'waitlist_registrations': waitlist_registrations,
        'conference_count': conference_count,
        'workshop_count': workshop_count,
        'social_count': social_count,
        'seminar_count': seminar_count,
        'title': 'Admin Dashboard'
    }
    
    return render(request, 'events/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_organizer)
@require_POST
def update_user_role(request):
    """Update user role"""
    user_id = request.POST.get('user_id')
    role = request.POST.get('role')
    
    if not user_id or not role:
        messages.error(request, 'Invalid request parameters.')
        return redirect('admin_dashboard')
    
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        user_profile.role = role
        user_profile.save()
        
        messages.success(request, f'User role updated successfully to {role}.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_or_organizer)
@require_POST
def upload_image(request):
    """Upload image to the image library"""
    if request.method == 'POST' and request.FILES.get('image'):
        form = ImageLibraryForm(request.POST, request.FILES)
        if form.is_valid():
            # Create new image but don't save to DB yet
            new_image = form.save(commit=False)
            new_image.uploaded_by = request.user
            new_image.save()
            
            messages.success(request, 'Image uploaded successfully.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        messages.error(request, 'No image file provided.')
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_or_organizer)
@require_POST
def delete_image(request, image_id):
    """Delete image from the image library"""
    image = get_object_or_404(ImageLibrary, id=image_id)
    
    # Check if user is admin or the uploader
    if request.user.profile.role == 'admin' or image.uploaded_by == request.user:
        image.image.delete(save=False)  # Delete the actual file
        image.delete()  # Delete the database record
        messages.success(request, 'Image deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this image.')
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin_or_organizer)
def get_image_details(request, image_id):
    """Get image details as JSON for AJAX requests"""
    image = get_object_or_404(ImageLibrary, id=image_id)
    
    data = {
        'id': image.id,
        'title': image.title,
        'category': image.category,
        'url': image.image.url,
        'description': image.description or '',
        'uploaded_by': image.uploaded_by.username,
        'upload_date': image.upload_date.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse(data)
