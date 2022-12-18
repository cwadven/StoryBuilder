from django.urls import path

from story.views import (
    SheetAnswerCheckAPIView,
    StoryPlayAPIView, SheetPlayAPIView,
)

app_name = 'story'

urlpatterns = [
    path('<int:story_id>/play', StoryPlayAPIView.as_view(), name='story_play'),
    path('sheet/<int:sheet_id>/play', SheetPlayAPIView.as_view(), name='sheet_play'),
    path('submit_answer', SheetAnswerCheckAPIView.as_view(), name='submit_answer'),
]
