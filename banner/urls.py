from django.urls import path

from banner.views import BannerListAPIView, BannerDetailAPIView

app_name = 'banner'

urlpatterns = [
    path('', BannerListAPIView.as_view(), name='banner_list'),
    path('<int:banner_id>', BannerDetailAPIView.as_view(), name='banner_detail'),
]
