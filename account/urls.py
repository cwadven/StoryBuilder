from django.urls import path

from account.views import SocialLoginView

urlpatterns = [
    path('social-login', SocialLoginView.as_view(), name='social_login'),
]
