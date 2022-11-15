from django.urls import path

from story.views import StoryPlayAPIView


app_name = 'story'

urlpatterns = [
    path('<int:story_id>/play', StoryPlayAPIView.as_view(), name='story_play'),
]
