from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Event, Booking, Review, UserProfile, MovieShowTime


class UserRegistrationForm(UserCreationForm):
    """User registration form with additional fields"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone (Optional)'
    }))
    is_organizer = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input'
    }), label='Register as Event Organizer')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update profile
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.is_organizer = self.cleaned_data.get('is_organizer', False)
            profile.save()
        
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    
    class Meta:
        model = Event
        fields = ['title', 'slug', 'description', 'category', 'event_type', 'venue', 'address', 
              'city', 'event_date', 'start_time', 'price', 'total_tickets', 
                  'image', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'event-slug'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Event Description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_event_type'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'total_tickets': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Tickets'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Validate date/time if needed
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        return cleaned_data


class BookingForm(forms.ModelForm):
    """Form for booking tickets"""
    
    class Meta:
        model = Booking
        fields = ['quantity', 'email', 'phone', 'show_time', 'selected_seats']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of Tickets',
                'min': '1'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email for Confirmation'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'show_time': forms.Select(attrs={'class': 'form-control'}),
            'selected_seats': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma separated seats e.g., A1,A2'})
        }
    
    def __init__(self, event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        
        if event:
            self.fields['quantity'].widget.attrs['max'] = event.available_tickets
            # If movie, populate show_time choices for this event
            if event.event_type == 'movie':
                self.fields['show_time'].queryset = MovieShowTime.objects.filter(event=event, show_date=event.event_date)
                self.fields['show_time'].required = True
                self.fields['selected_seats'].required = False
            else:
                # non-movie events don't use show_time
                self.fields['show_time'].queryset = MovieShowTime.objects.none()
                self.fields['show_time'].required = False
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        
        if self.event:
            if self.event.event_type == 'movie':
                show_time = self.cleaned_data.get('show_time')
                if show_time and quantity > show_time.available_tickets:
                    raise forms.ValidationError(f"Only {show_time.available_tickets} tickets available for selected show time")
            else:
                if quantity > self.event.available_tickets:
                    raise forms.ValidationError(
                        f"Only {self.event.available_tickets} tickets available"
                    )
        
        return quantity


class ReviewForm(forms.ModelForm):
    """Form for submitting event reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(1, 6)], attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }


class QRCodeValidationForm(forms.Form):
    """Form for validating QR codes"""
    verification_code = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Verification Code or Scan QR',
            'autofocus': True
        })
    )
