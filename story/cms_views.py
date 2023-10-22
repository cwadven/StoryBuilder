from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import pagination
from config.permissions.cms_permissions import CMSUserPermission
from hint.services import get_available_sheet_hints_count
from story.cmd_dtos import (
    CMSStoryListItemDTO,
    CMSStoryListResponse,
    CMSStorySheetAnswerMapItemDTO,
    CMSStorySheetAnswerMapResponse,
    CMSStorySheetMapItemDTO,
    CMSStorySheetMapResponse,
)
from story.cms_services import (
    get_active_sheets,
    get_sheet_answer_ids_by_sheet_ids,
    get_sheet_answers_by_sheet_ids,
    get_stories_qs,
    get_story_search_filter,
)


class CMSStoryListAPIView(APIView):
    permission_classes = [CMSUserPermission]

    @pagination(default_size=20)
    def get(self, request, start_row, end_row):
        search_type = request.GET.get('search_type', '')
        search_value = request.GET.get('search_value', '')
        order_by = request.GET.get('order_by', '-id')

        stories_qs = get_stories_qs().select_related(
            'author'
        ).filter(
            get_story_search_filter(search_type, search_value)
        )

        total_count = stories_qs.count()
        cms_stories = stories_qs.order_by(order_by)[start_row:end_row]

        return Response(
            data=CMSStoryListResponse(
                total_count=total_count,
                stories=[
                    CMSStoryListItemDTO.of(story).to_dict()
                    for story in cms_stories
                ]
            ).to_dict(),
            status=200,
        )


class CMSStorySheetMapAPIView(APIView):
    permission_classes = [CMSUserPermission]

    def get(self, request, story_id):
        active_sheet_qs = list(get_active_sheets(story_id))
        sheet_ids = [sheet.id for sheet in active_sheet_qs]
        hint_count_by_sheet_id = get_available_sheet_hints_count(sheet_ids)
        sheet_answer_ids_by_sheet_id = get_sheet_answer_ids_by_sheet_ids(sheet_ids)
        return Response(
            data=CMSStorySheetMapResponse(
                sheets=[
                    CMSStorySheetMapItemDTO.of(
                        sheet=sheet,
                        hint_count=hint_count_by_sheet_id[sheet.id],
                        answer_ids=sheet_answer_ids_by_sheet_id[sheet.id],
                    )
                    for sheet in active_sheet_qs
                ],
            ).to_dict(),
            status=200,
        )


class CMSStorySheetAnswerMapAPIView(APIView):
    permission_classes = [CMSUserPermission]

    def get(self, request, story_id):
        return Response(
            data=CMSStorySheetAnswerMapResponse(
                answers=[
                    CMSStorySheetAnswerMapItemDTO.of(sheet_answer=sheet_answer)
                    for sheet_answer in get_sheet_answers_by_sheet_ids(
                        [sheet.id for sheet in get_active_sheets(story_id)]
                    )
                ],
            ).to_dict(),
            status=200,
        )
