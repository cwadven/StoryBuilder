from django.urls import path

from story.cms_views import CMSStoryListAPIView

app_name = 'cms_story'


urlpatterns = [
    path('', CMSStoryListAPIView.as_view(), name='story_cms'),
]
