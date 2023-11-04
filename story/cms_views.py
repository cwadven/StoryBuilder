import itertools

from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import pagination, optionals
from common_library import get_integers_from_string
from config.permissions.cms_permissions import CMSUserPermission
from hint.services import get_available_sheet_hints_count
from story.cmd_dtos import (
    CMSStoryAnswerNextPathMapItemDTO,
    CMSStoryAnswerNextPathMapResponse,
    CMSStoryListItemDTO,
    CMSStoryListResponse,
    CMSStorySheetAnswerMapItemDTO,
    CMSStorySheetAnswerMapResponse,
    CMSStorySheetMapItemDTO,
    CMSStorySheetMapResponse, CMSStoryAnswerNextPathItemDTO,
)
from story.cms_services import (
    get_active_sheets,
    get_next_sheet_paths_by_sheet_answer_ids,
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


class CMSStoryAnswerNextPathMapAPIView(APIView):
    permission_classes = [CMSUserPermission]

    @optionals({'answer_ids': ''})
    def get(self, request, story_id, o):
        answer_ids = get_integers_from_string(o['answer_ids'], True)
        answer_ids_by_sheet_id = get_sheet_answer_ids_by_sheet_ids(
            [sheet.id for sheet in list(get_active_sheets(story_id))]
        )
        answer_ids_for_sheet = list(itertools.chain(*answer_ids_by_sheet_id.values()))
        if not answer_ids:
            answer_ids = answer_ids_for_sheet
        else:
            answer_ids = set(answer_ids_for_sheet) & set(answer_ids)

        next_sheet_paths_by_sheet_answer_ids = get_next_sheet_paths_by_sheet_answer_ids(answer_ids)
        return Response(
            data=CMSStoryAnswerNextPathMapResponse(
                answer_next_paths=[
                    CMSStoryAnswerNextPathMapItemDTO(
                        answer_id=sheet_answer_id,
                        next_paths=[
                            CMSStoryAnswerNextPathItemDTO(
                                sheet_id=next_sheet_path.sheet_id,
                                quantity=next_sheet_path.quantity,
                            ) for next_sheet_path in next_sheet_paths
                        ]
                    )
                    for sheet_answer_id, next_sheet_paths in next_sheet_paths_by_sheet_answer_ids.items()
                ],
            ).to_dict(),
            status=200,
        )
