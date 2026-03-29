from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("me/", views.ProfileDetailView.as_view(), name="profile-detail"),
    path("me/edit/", views.ProfileUpdateView.as_view(), name="profile-edit"),
]
