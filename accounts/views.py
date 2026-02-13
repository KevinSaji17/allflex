from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from .forms import SignUpForm
from django.http import HttpResponseRedirect
from .models import UserProfile

# Create your views here.

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # MVP: give new members demo credits so they can try "Use 1 visit"
        self.object.credits = 25
        self.object.save(update_fields=['credits'])
        return response

def role_based_redirect(request):
    if request.user.is_authenticated:
        # Since UserProfile is the custom user model, access role directly
        if request.user.role == 'admin':
            return HttpResponseRedirect(reverse('admin_dashboard'))
        elif request.user.role == 'gym_owner':  # CORRECT role name
            return HttpResponseRedirect(reverse('gym_dashboard'))
        else:
            # Regular user is redirected to their dashboard
            return HttpResponseRedirect(reverse('user_dashboard'))  # CHANGED from 'home' to 'user_dashboard'
    # Non-authenticated users go to home
    return HttpResponseRedirect(reverse('home'))
