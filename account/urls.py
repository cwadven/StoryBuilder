from django.urls import path

from account.views import SocialLoginView, SignUpView, SignUpEmailTokenSendView

urlpatterns = [
    path('social-login', SocialLoginView.as_view(), name='social_login'),
    path('sign-up', SignUpView.as_view(), name='sign_up'),
    path('sign-up-check', SignUpEmailTokenSendView.as_view(), name='sign_up_check'),
]
