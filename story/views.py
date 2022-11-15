from rest_framework.response import Response
from rest_framework.views import APIView

from story.dtos import PlayingSheetDTO
from story.services import get_running_start_sheet_by_story


class StoryPlayAPIView(APIView):
    def get(self, request, story_id):
        start_sheet = get_running_start_sheet_by_story(story_id)
        playing_sheet = PlayingSheetDTO.of(start_sheet).to_dict()
        return Response(playing_sheet, status=200)
