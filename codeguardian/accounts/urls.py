from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UserProfileView

urlpatterns = [
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("api/auth/me/", UserProfileView.as_view(), name="auth-me"),
]
