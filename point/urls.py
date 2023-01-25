from django.urls import path

from point.views import UserPointAPIView


app_name = 'point'

urlpatterns = [
    path('user', UserPointAPIView.as_view(), name='user_point_info'),
]
