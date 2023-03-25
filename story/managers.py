from django.contrib.auth.models import AnonymousUser
from django.db.models import Manager, Q, Exists, OuterRef


class StoryManager(Manager):
    def get_actives(self, user=None):
        base_query = self.filter(
            is_deleted=False,
            displayable=True,
        )
        if user and not isinstance(user, AnonymousUser):
            secret_member_condition = Exists(
                user.secret_stories.filter(pk=OuterRef('pk'))
            )
            base_query = base_query.filter(
                Q(is_secret=False) | secret_member_condition,
            )
        else:
            base_query = base_query.filter(is_secret=False)

        return base_query


class PopularStoryManager(Manager):
    def get_actives(self, user=None):
        base_query = self.filter(
            story__is_deleted=False,
            story__displayable=True,
            is_deleted=False,
        )
        if user and not isinstance(user, AnonymousUser):
            secret_member_condition = Exists(
                user.secret_stories.filter(pk=OuterRef('story_id'))
            )
            base_query = base_query.filter(
                Q(story__is_secret=False) | secret_member_condition,
            )
        else:
            base_query = base_query.filter(story__is_secret=False)

        return base_query
