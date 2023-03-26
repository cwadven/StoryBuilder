# Generated by Django 3.2.16 on 2023-03-25 22:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0016_alter_story_is_secret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='secret_members',
            field=models.ManyToManyField(blank=True, null=True, related_name='secret_stories', to=settings.AUTH_USER_MODEL),
        ),
    ]