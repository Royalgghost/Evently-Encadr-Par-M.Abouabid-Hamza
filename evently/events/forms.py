from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, Venue, UserProfile, EventRegistration, ImageLibrary
from django.utils import timezone

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone_number', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'city', 'capacity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EventForm(forms.ModelForm):
    # Add datepicker and time widgets
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text="Event start date and time"
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text="Event end date and time"
    )
    registration_deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=False,
        help_text="Deadline for registration (optional)"
    )
    
    # Make slug optional so we can auto-generate it
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="URL-friendly name (leave blank to auto-generate from title)"
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'slug', 'description', 'category', 
            'venue', 'location_address', 'start_date', 
            'end_date', 'capacity', 'poster_image', 
            'registration_deadline', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.Select(attrs={'class': 'form-select'}),
            'location_address': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'poster_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_deadline = cleaned_data.get('registration_deadline')
        
        # Validate dates
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date")
        
        if registration_deadline and start_date and registration_deadline > start_date:
            raise forms.ValidationError("Registration deadline must be before event start date")
        
        return cleaned_data

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = []  # We don't need any fields in the form as we'll set them in the view
        
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if event has available seats
        if self.event and self.event.available_seats() <= 0:
            raise forms.ValidationError("This event is fully booked.")
        
        # Check if registration is still open
        if self.event and not self.event.is_registration_open():
            raise forms.ValidationError("Registration for this event is closed.")
        
        # Check if user is already registered
        if self.event and self.user and EventRegistration.objects.filter(event=self.event, participant=self.user).exists():
            raise forms.ValidationError("You are already registered for this event.")
        
        return cleaned_data

class EventFilterForm(forms.Form):
    FILTER_CHOICES = (
        ('', 'All Events'),
        ('upcoming', 'Upcoming Events'),
        ('past', 'Past Events'),
    )
    
    # Import the EVENT_CATEGORIES from the module level, not from the Event class
    from .models import EVENT_CATEGORIES
    
    filter_by = forms.ChoiceField(choices=FILTER_CHOICES, required=False)
    category = forms.ChoiceField(choices=[('', 'All Categories')] + list(EVENT_CATEGORIES), required=False)
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    search = forms.CharField(required=False, max_length=100)

class ImageLibraryForm(forms.ModelForm):
    class Meta:
        model = ImageLibrary
        fields = ['title', 'image', 'category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
