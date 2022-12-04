from django.urls import path

from story.views import (
    SheetAnswerCheckAPIView,
    StoryPlayAPIView,
)

app_name = 'story'

urlpatterns = [
    path('<int:story_id>/play', StoryPlayAPIView.as_view(), name='story_play'),
    path('submit_answer', SheetAnswerCheckAPIView.as_view(), name='submit_answer'),
]
