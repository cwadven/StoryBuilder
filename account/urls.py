from django.urls import path

from account.views import SocialLoginView, SignUpEmailTokenSendView, SignUpValidationView

urlpatterns = [
    path('social-login', SocialLoginView.as_view(), name='social_login'),
    path('sign-up-validation', SignUpValidationView.as_view(), name='sign_up_validation'),
    path('sign-up-check', SignUpEmailTokenSendView.as_view(), name='sign_up_check'),
]
