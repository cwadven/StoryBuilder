from rest_framework.exceptions import APIException

from config.common.exception_codes import StartingSheetDoesNotExists
from story.models import Sheet


def get_running_start_sheet_by_story(story_id):
    """
    Story 에서 시작하는 처음 Sheet 가져오기
    """
    try:
        return Sheet.objects.get(
            story_id=story_id,
            story__is_deleted=False,
            story__displayable=True,
            is_start=True,
            is_deleted=False
        )
    except Sheet.DoesNotExist:
        raise StartingSheetDoesNotExists()
