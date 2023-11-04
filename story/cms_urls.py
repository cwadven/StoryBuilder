from django.urls import path

from story.cms_views import (
    CMSStoryAnswerNextPathMapAPIView,
    CMSStoryListAPIView,
    CMSStorySheetAnswerMapAPIView,
    CMSStorySheetMapAPIView,
)

app_name = 'cms_story'


urlpatterns = [
    path('', CMSStoryListAPIView.as_view(), name='story_cms'),
    path('<int:story_id>/sheet/map', CMSStorySheetMapAPIView.as_view(), name='sheet_cms_map'),
    path('<int:story_id>/answer/map', CMSStorySheetAnswerMapAPIView.as_view(), name='answer_cms_map'),
    path('<int:story_id>/next-path/map', CMSStoryAnswerNextPathMapAPIView.as_view(), name='answer_next_path_cms_map'),
]
