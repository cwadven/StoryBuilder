from rest_framework.exceptions import ValidationError

from account.constants import UserCreationExceptionMessage
from account.services import is_username_exists, is_email_exists, is_nickname_exists
from common_library import PayloadValidator


class SignUpPayloadValidator(PayloadValidator):
    def __init__(self, payload):
        super(SignUpPayloadValidator, self).__init__(payload)

    def validate(self):
        if is_username_exists(self.payload['username']):
            self.add_error_context('username', UserCreationExceptionMessage.USERNAME_EXISTS.label)
        if is_nickname_exists(self.payload['nickname']):
            self.add_error_context('nickname', UserCreationExceptionMessage.NICKNAME_EXISTS.label)
        if is_email_exists(self.payload['email']):
            self.add_error_context('email', UserCreationExceptionMessage.EMAIL_EXISTS.label)
        if self.payload['password1'] != self.payload['password2']:
            self.add_error_context('password2', UserCreationExceptionMessage.CHECK_PASSWORD.label)

        if self.error_context:
            raise ValidationError(self.error_context)
