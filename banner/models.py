from django.db import models

from banner.managers import BannerManager


class BannerType(models.Model):
    name = models.CharField(unique=True, max_length=45, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class Banner(models.Model):
    title = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    background_image = models.TextField(blank=True, null=True)
    background_color = models.TextField(blank=True, null=True)
    banner_type = models.ForeignKey(BannerType, models.SET_NULL, blank=True, null=True)
    sequence = models.PositiveIntegerField(db_index=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BannerManager()

    def __str__(self):
        return f'{self.title}'
