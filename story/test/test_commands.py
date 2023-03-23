from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from datetime import datetime

from account.models import User
from story.models import Story, StoryLike, PopularStory


class PopularStoryCommandTestCase(TestCase):
    def setUp(self):
        super(PopularStoryCommandTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.story1 = Story.objects.create(
            author=self.user,
            title='test_story1',
            description='test_description1',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.story2 = Story.objects.create(
            author=self.user,
            title='test_story2',
            description='test_description2',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.story3 = Story.objects.create(
            author=self.user,
            title='test_story3',
            description='test_description3',
            image='https://image.test',
            background_image='https://image.test',
        )

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            'update_popular_story',
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_create_popular_stories(self):
        # Given: story1 좋아요 1개, story2 좋아요 2개, story3 좋아요 3개
        stories = [self.story1, self.story2, self.story2, self.story3, self.story3, self.story3]
        for story in stories:
            StoryLike.objects.create(
                user=self.user,
                story=story,
            )

        # When: update_popular_story command 실행
        self.call_command()

        # Then: 3개의 PopularStory 쌓임
        qs = PopularStory.objects.all().order_by('rank')
        self.assertEqual(qs.count(), 3)
        # And: story3, story2, story1 순으로 rank 가 매겨짐
        self.assertEqual(qs[0].story, self.story3)
        self.assertEqual(qs[0].rank, 1)
        self.assertEqual(qs[0].like_count, 3)
        self.assertEqual(qs[1].story, self.story2)
        self.assertEqual(qs[1].rank, 2)
        self.assertEqual(qs[1].like_count, 2)
        self.assertEqual(qs[2].story, self.story1)
        self.assertEqual(qs[2].rank, 3)
        self.assertEqual(qs[2].like_count, 1)

    def test_create_popular_stories_check_if_before_ranks_are_deleted(self):
        # Given: story1 좋아요 1개, story2 좋아요 2개, story3 좋아요 3개
        stories = [self.story1, self.story2, self.story2, self.story3, self.story3, self.story3]
        for story in stories:
            StoryLike.objects.create(
                user=self.user,
                story=story,
            )

        # When: update_popular_story command 실행
        self.call_command()

        qs = PopularStory.objects.all().order_by('rank')
        # Then: 3개의 PopularStory 쌓임
        self.assertEqual(qs.count(), 3)
        # And: story3, story2, story1 순으로 rank 가 매겨짐
        self.assertEqual(qs[0].story, self.story3)
        self.assertEqual(qs[0].rank, 1)
        self.assertEqual(qs[0].like_count, 3)
        self.assertEqual(qs[1].story, self.story2)
        self.assertEqual(qs[1].rank, 2)
        self.assertEqual(qs[1].like_count, 2)
        self.assertEqual(qs[2].story, self.story1)
        self.assertEqual(qs[2].rank, 3)
        self.assertEqual(qs[2].like_count, 1)

        # When: update_popular_story command 1번 더 실행
        self.call_command()

        qs = PopularStory.objects.all().order_by('rank')
        # Then: 6개의 PopularStory 쌓임
        self.assertEqual(qs.count(), 6)
        # And: 기존것 삭제 후 story3, story2, story1 순으로 rank 가 매겨짐
        qs = qs.filter(is_deleted=True)
        self.assertEqual(qs.count(), 3)
        self.assertEqual(qs[0].story, self.story3)
        self.assertEqual(qs[0].rank, 1)
        self.assertEqual(qs[0].like_count, 3)
        self.assertEqual(qs[1].story, self.story2)
        self.assertEqual(qs[1].rank, 2)
        self.assertEqual(qs[1].like_count, 2)
        self.assertEqual(qs[2].story, self.story1)
        self.assertEqual(qs[2].rank, 3)
        self.assertEqual(qs[2].like_count, 1)

    def test_create_popular_stories_when_rank_on_it(self):
        # Given: story1 좋아요 1개, story2 좋아요 2개, story3 좋아요 3개
        stories = [self.story1, self.story2, self.story2, self.story3, self.story3, self.story3]
        for story in stories:
            StoryLike.objects.create(
                user=self.user,
                story=story,
            )

        # When: update_popular_story command 실행 (rank=2)
        self.call_command(rank=2)

        # Then: 2개의 PopularStory 쌓임
        qs = PopularStory.objects.all().order_by('rank')
        self.assertEqual(qs.count(), 2)
        # And: story3, story2 순으로 rank 가 매겨짐
        self.assertEqual(qs[0].story, self.story3)
        self.assertEqual(qs[0].rank, 1)
        self.assertEqual(qs[0].like_count, 3)
        self.assertEqual(qs[1].story, self.story2)
        self.assertEqual(qs[1].rank, 2)
        self.assertEqual(qs[1].like_count, 2)

    def test_create_popular_stories_when_second_on_it(self):
        # Given: story1 좋아요 1개, story2 좋아요 2개, story3 좋아요 3개
        stories = [self.story1, self.story2, self.story2, self.story3, self.story3, self.story3]
        for story in stories:
            StoryLike.objects.create(
                user=self.user,
                story=story,
            )
        # And: story1 의 like 를 과거 초로 생성
        StoryLike.objects.filter(story=self.story1).update(updated_at=datetime(2017, 1, 1))

        # When: update_popular_story command 실행 (second=50)
        self.call_command(second=50)

        # Then: 2개의 PopularStory 쌓임
        qs = PopularStory.objects.all().order_by('rank')
        self.assertEqual(qs.count(), 2)
        # And: story1은 포함이 안되고 story3, story2 순으로 rank 가 매겨짐
        self.assertEqual(qs[0].story, self.story3)
        self.assertEqual(qs[0].rank, 1)
        self.assertEqual(qs[0].like_count, 3)
        self.assertEqual(qs[1].story, self.story2)
        self.assertEqual(qs[1].rank, 2)
        self.assertEqual(qs[1].like_count, 2)
