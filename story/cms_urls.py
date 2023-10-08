from django.urls import path

from story.cms_views import (
    CMSStoryListAPIView,
    CMSStorySheetMapAPIView,
)

app_name = 'cms_story'


urlpatterns = [
    path('', CMSStoryListAPIView.as_view(), name='story_cms'),
    path('<int:story_id>/sheet/map', CMSStorySheetMapAPIView.as_view(), name='sheet_cms_map'),
]
