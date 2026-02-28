from django import forms
from django.contrib.auth.forms import UserCreationForm
from .db_utils import is_mongodb

# Import UserProfile model for SQLite mode (safe to import even in MongoDB mode)
from .models import UserProfile as SQLiteUserProfile


# SQLite Form - uses Django's UserCreationForm (ModelForm)
class SQLiteSignUpForm(UserCreationForm):
    """SignUpForm for SQLite database mode"""
    
    class Meta(UserCreationForm.Meta):
        model = SQLiteUserProfile
        fields = ('username', 'email')  # Role removed - determined by button clicked


# MongoDB Form - plain Form (not ModelForm)
class MongoSignUpForm(forms.Form):
    """SignUpForm for MongoDB mode - doesn't use ModelForm"""
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'At least 8 characters'}),
        help_text='Your password must contain at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        help_text='Enter the same password as before, for verification.'
    )
    
    def clean_username(self):
        """Check if username already exists"""
        username = self.cleaned_data.get('username')
        if username:
            from .mongo_models import UserProfile
            if UserProfile.objects(username=username).first():
                raise forms.ValidationError('A user with that username already exists.')
        return username
    
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if email:
            from .mongo_models import UserProfile
            if UserProfile.objects(email=email).first():
                raise forms.ValidationError('A user with that email already exists.')
        return email
    
    def clean(self):
        """Validate that passwords match"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        
        return cleaned_data


# Dynamic form selector
def get_signup_form():
    """Return appropriate SignUpForm based on database mode"""
    if is_mongodb():
        return MongoSignUpForm
    else:
        return SQLiteSignUpForm


# Alias for backward compatibility
SignUpForm = get_signup_form() 