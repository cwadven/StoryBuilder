from rest_framework.exceptions import ValidationError

from account.constants import (
    UserCreationExceptionMessage,
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    NICKNAME_MIN_LENGTH,
    NICKNAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)
from account.services import (
    is_username_exists,
    is_email_exists,
    is_nickname_exists,
    is_email_reg_exp_valid,
    is_length_valid,
    is_only_alphanumeric,
    is_only_korean_english_alphanumeric,
)
from common_library import PayloadValidator


class SignUpPayloadValidator(PayloadValidator):
    def __init__(self, payload):
        super(SignUpPayloadValidator, self).__init__(payload)

    def validate(self):
        # username
        if is_username_exists(self.payload['username']):
            self.add_error_context('username', UserCreationExceptionMessage.USERNAME_EXISTS.label)
        if not is_length_valid(self.payload['username'], USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH):
            self.add_error_context(
                'username',
                UserCreationExceptionMessage.USERNAME_LENGTH_INVALID.label.format(
                    USERNAME_MIN_LENGTH,
                    USERNAME_MAX_LENGTH,
                )
            )
        if not is_only_alphanumeric(self.payload['username']):
            self.add_error_context(
                'username',
                UserCreationExceptionMessage.USERNAME_REG_EXP_INVALID.label
            )
        # nickname
        if is_nickname_exists(self.payload['nickname']):
            self.add_error_context('nickname', UserCreationExceptionMessage.NICKNAME_EXISTS.label)
        if not is_length_valid(self.payload['nickname'], NICKNAME_MIN_LENGTH, NICKNAME_MAX_LENGTH):
            self.add_error_context(
                'nickname',
                UserCreationExceptionMessage.NICKNAME_LENGTH_INVALID.label.format(
                    NICKNAME_MIN_LENGTH,
                    NICKNAME_MAX_LENGTH,
                )
            )
        if not is_only_korean_english_alphanumeric(self.payload['nickname']):
            self.add_error_context(
                'nickname',
                UserCreationExceptionMessage.NICKNAME_REG_EXP_INVALID.label
            )
        # email
        if is_email_exists(self.payload['email']):
            self.add_error_context('email', UserCreationExceptionMessage.EMAIL_EXISTS.label)
        if not is_email_reg_exp_valid(self.payload['email']):
            self.add_error_context('email', UserCreationExceptionMessage.EMAIL_REG_EXP_INVALID.label)
        # password
        if not is_length_valid(self.payload['password1'], PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH):
            self.add_error_context(
                'password1',
                UserCreationExceptionMessage.PASSWORD_LENGTH_INVALID.label.format(
                    PASSWORD_MIN_LENGTH,
                    PASSWORD_MAX_LENGTH,
                )
            )
        if self.payload['password1'] != self.payload['password2']:
            self.add_error_context('password2', UserCreationExceptionMessage.CHECK_PASSWORD.label)

        if self.error_context:
            raise ValidationError(self.error_context)
