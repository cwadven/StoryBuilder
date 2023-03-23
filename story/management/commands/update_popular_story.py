from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count

from story.models import StoryLike, PopularStory


class Command(BaseCommand):
    help = 'Popular Story 최신화'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.second = None
        self.rank = None

    def add_arguments(self, parser):
        # 키워드 인자 (named arguments)
        parser.add_argument('-s', '--second', type=int, help='현재 시간에서 필터링할 범위 (기본 1시간)', default=3600)
        parser.add_argument('-r', '--rank', type=int, help='상위 몇개 가져올지 설정', default=6)

    def handle(self, *args, **kwargs):
        self.second = kwargs.get('second')
        self.rank = kwargs.get('rank')

        top_stories = self.get_top_stories()

        self.delete_old_popular_stories()
        self.create_new_popular_stories(top_stories)

        self.stdout.write('success')

    def get_top_stories(self):
        return StoryLike.objects.filter(
            is_deleted=False,
            updated_at__gte=datetime.now() - timedelta(seconds=self.second),
        ).values(
            'story'
        ).annotate(
            total=Count('story')
        ).values_list(
            'story',
            'total',
        ).order_by(
            '-total'
        )[:self.rank]

    @staticmethod
    def delete_old_popular_stories():
        PopularStory.objects.filter(
            is_deleted=False,
        ).update(
            is_deleted=True,
            updated_at=datetime.now(),
        )

    def create_new_popular_stories(self, top_popular_stories):
        popular_stories = [
            PopularStory(
                rank=rank,
                like_count=story[1],
                base_past_second=self.second,
                story_id=story[0],
            ) for rank, story in enumerate(top_popular_stories, 1)
        ]
        PopularStory.objects.bulk_create(popular_stories)
