from django.contrib.auth import login

from account.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

from common_decorator import mandatories
from common_library import get_login_token


class SocialLoginView(APIView):
    @mandatories('provider', 'token')
    def post(self, request, m):
        user, is_created = User.objects.get_or_create_user_by_token(m['token'], m['provider'])
        user.raise_if_inaccessible()

        login(request, user)

        context = {
            'accessToken': get_login_token(user),
            'isCreated': is_created,
        }

        return Response(context, status=200)
