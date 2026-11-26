from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.authentication import views
from apps.utils import postCreate


urlpatterns = [
    path("signup/", views.SignupView.as_view(postCreate), name="signup"),
    path("login/", views.LoginView.as_view(postCreate), name="login"),
    path("login/google/", views.GoogleLoginView.as_view(), name="google_login"),
    path(
        "change-password/",
        views.UserChangePasswordView.as_view(postCreate),
        name="change_password",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="verify_jwt"),
    path("logout/", views.LogoutView.as_view(postCreate), name="logout"),
]
