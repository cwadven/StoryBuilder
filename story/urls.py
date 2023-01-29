from django.urls import path

from story.views import (
    SheetAnswerCheckAPIView,
    StoryPlayAPIView,
    SheetPlayAPIView,
    StoryPlayGetRecentUnsolvedSheetAPIView,
)


app_name = 'story'

urlpatterns = [
    path('<int:story_id>/play', StoryPlayAPIView.as_view(), name='story_play'),
    path('<int:story_id>/recent-play-sheet', StoryPlayGetRecentUnsolvedSheetAPIView.as_view(), name='get_recent_play_sheet'),
    path('sheet/<int:sheet_id>/play', SheetPlayAPIView.as_view(), name='sheet_play'),
    path('submit_answer', SheetAnswerCheckAPIView.as_view(), name='submit_answer'),
]
