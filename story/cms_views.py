from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import pagination
from story.cmd_dtos import (
    CMSStoryListItemDTO,
    CMSStoryListResponse,
)
from story.cms_services import (
    get_stories_qs,
    get_story_search_filter,
)


class CMSStoryListAPIView(APIView):
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
