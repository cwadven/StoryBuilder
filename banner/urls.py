from django.urls import path

from banner.views import BannerListAPIView


app_name = 'banner'

urlpatterns = [
    path('', BannerListAPIView.as_view(), name='banner_list'),
]
