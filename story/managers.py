from django.db.models import Manager, Q


class StoryManager(Manager):
    def get_actives(self, user=None):
        return self.filter(
            is_deleted=False,
            displayable=True,
        ).filter(
            Q(is_secret=False) | Q(secret_members=user),
        )


class PopularStoryManager(Manager):
    def get_actives(self, user=None):
        return self.filter(
            story__is_deleted=False,
            story__displayable=True,
            is_deleted=False,
        ).filter(
            Q(story__is_secret=False) | Q(story__secret_members=user),
        )
