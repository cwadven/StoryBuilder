from django.test import TestCase

from account.models import User
from story.models import Story, PopularStory


class TestStoryManager(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.story1 = Story.objects.create(
            author=self.user1,
            title='Active Story',
            is_secret=False,
            is_deleted=False,
            displayable=True,
        )
        self.story2 = Story.objects.create(
            author=self.user1,
            title='Deleted Story',
            is_secret=False,
            is_deleted=True,
            displayable=True,
        )
        self.story3 = Story.objects.create(
            author=self.user1,
            title='Not Displayable Story',
            is_secret=False,
            is_deleted=False,
            displayable=False,
        )

    def test_get_actives_is_secret(self):
        # Given:
        story1 = Story.objects.create(
            author=self.user1,
            title='Public Story',
            is_secret=False,
        )
        story2 = Story.objects.create(
            author=self.user1,
            title='Secret Story',
            is_secret=True,
        )
        story2.secret_members.add(self.user1)
        story2.save()

        # When: 모든 사용자에게 공개된 Story 객체 검색
        active_stories_for_all = Story.objects.get_actives()
        # Then:
        self.assertIn(story1, active_stories_for_all)
        self.assertNotIn(story2, active_stories_for_all)

        # When: user1에게 공개된 Story 객체 검색
        active_stories_for_user1 = Story.objects.get_actives(user=self.user1)
        # Then:
        self.assertIn(story1, active_stories_for_user1)
        self.assertIn(story2, active_stories_for_user1)

        # When: user2에게 공개된 Story 객체 검색
        active_stories_for_user2 = Story.objects.get_actives(user=self.user2)
        # Then:
        self.assertIn(story1, active_stories_for_user2)
        self.assertNotIn(story2, active_stories_for_user2)

    def test_get_actives_is_deleted(self):
        # When: is_deleted 필터 테스트
        active_stories = Story.objects.get_actives()

        # Then:
        self.assertIn(self.story1, active_stories)
        self.assertNotIn(self.story2, active_stories)

    def test_get_actives_displayable(self):
        # When: displayable 필터 테스트
        active_stories = Story.objects.get_actives()

        # Then:
        self.assertIn(self.story1, active_stories)
        self.assertNotIn(self.story3, active_stories)


class TestPopularStoryManager(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.story1 = Story.objects.create(
            author=self.user1,
            title='Active Story',
            is_secret=False,
            is_deleted=False,
            displayable=True,
        )
        self.story2 = Story.objects.create(
            author=self.user1,
            title='Deleted Story',
            is_secret=False,
            is_deleted=True,
            displayable=True,
        )
        self.story3 = Story.objects.create(
            author=self.user1,
            title='Not Displayable Story',
            is_secret=False,
            is_deleted=False,
            displayable=False,
        )
        self.popular_story1 = PopularStory.objects.create(
            story=self.story1,
            rank=1,
            like_count=1,
            base_past_second=1,
        )
        self.popular_story2 = PopularStory.objects.create(
            story=self.story2,
            rank=2,
            like_count=1,
            base_past_second=1,
        )
        self.popular_story3 = PopularStory.objects.create(
            story=self.story3,
            rank=3,
            like_count=1,
            base_past_second=1,
        )

    def test_get_actives_is_secret(self):
        # Given:
        story1 = Story.objects.create(
            author=self.user1,
            title='Public Story',
            is_secret=False,
        )
        story2 = Story.objects.create(
            author=self.user1,
            title='Secret Story',
            is_secret=True,
        )
        popular_story1 = PopularStory.objects.create(
            story=story1,
            rank=1,
            like_count=1,
            base_past_second=1,
        )
        popular_story2 = PopularStory.objects.create(
            story=story2,
            rank=2,
            like_count=1,
            base_past_second=1,
        )
        story2.secret_members.add(self.user1)
        story2.save()

        # When: 모든 사용자에게 공개된 PopularStory 객체 검색
        active_popular_stories_for_all = PopularStory.objects.get_actives()
        # Then:
        self.assertIn(popular_story1, active_popular_stories_for_all)
        self.assertNotIn(popular_story2, active_popular_stories_for_all)

        # When: user1에게 공개된 PopularStory 객체 검색
        active_popular_stories_for_user1 = PopularStory.objects.get_actives(user=self.user1)
        # Then:
        self.assertIn(popular_story1, active_popular_stories_for_user1)
        self.assertIn(popular_story2, active_popular_stories_for_user1)

        # When: user2에게 공개된 PopularStory 객체 검색
        active_popular_stories_for_user2 = PopularStory.objects.get_actives(user=self.user2)
        # Then:
        self.assertIn(popular_story1, active_popular_stories_for_user2)
        self.assertNotIn(popular_story2, active_popular_stories_for_user2)

    def test_get_actives_is_deleted(self):
        # Given:
        self.popular_story3.is_deleted = True
        self.popular_story3.save()

        # When: is_deleted 필터 테스트
        active_popular_stories = PopularStory.objects.get_actives()

        # Then:
        self.assertIn(self.popular_story1, active_popular_stories)
        self.assertNotIn(self.popular_story2, active_popular_stories)
        self.assertNotIn(self.popular_story3, active_popular_stories)

    def test_get_actives_displayable(self):
        # When: displayable 필터 테스트
        active_popular_stories = PopularStory.objects.get_actives()

        # Then:
        self.assertIn(self.popular_story1, active_popular_stories)
        self.assertNotIn(self.popular_story3, active_popular_stories)
