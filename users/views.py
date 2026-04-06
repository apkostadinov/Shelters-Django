from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from accounts.models import Volunteer
from .forms import UserProfileForm, UserRegistrationForm
from .models import User


class SignUpView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object
        full_name = f"{user.first_name} {user.last_name}".strip()
        Volunteer.objects.get_or_create(
            user=user,
            defaults={
                "name": full_name or user.username,
                "email": user.email,
                "phone_number": user.phone_number or "",
                "experience_level": "beginner",
            },
        )
        return response


class UserLoginView(LoginView):
    template_name = "users/login.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("homepage")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("profile-detail")

    def get_object(self, queryset=None):
        return self.request.user

    def test_func(self):
        return self.request.user.is_authenticated


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/profile_confirm_delete.html"
    success_url = reverse_lazy("homepage")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.get_object()
        logout(self.request)
        user.delete()
        return HttpResponseRedirect(self.get_success_url())
