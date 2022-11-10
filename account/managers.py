from django.contrib.auth.models import UserManager

from account.constants import SocialTypeSelector
from account.helpers.social_login_helpers import SocialLoginController


class CustomUserManager(UserManager):
    def get_or_create_user_by_token(self, token: str, provider: int) -> tuple:
        is_created = False
        data = SocialLoginController(
            SocialTypeSelector(int(provider)).selector()
        ).validate(token)

        try:
            user = self.get(
                username=data['id'],
                user_provider_id=provider,
            )
        except self.model.DoesNotExist:
            user = self.create(
                username=data['id'],
                user_type_id=3,
                user_status_id=1,
                user_provider_id=provider,
            )
            is_created = True

        return user, is_created
