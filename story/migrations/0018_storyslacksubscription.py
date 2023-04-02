# Generated by Django 3.2.16 on 2023-04-02 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0017_alter_story_secret_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorySlackSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slack_webhook_url', models.CharField(max_length=300, verbose_name='웹훅 url')),
                ('slack_channel_description', models.CharField(max_length=300, verbose_name='웹훅을 쏠 channel 소개')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('respondent_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('story', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.story')),
            ],
            options={
                'verbose_name': 'Story 관전을 위한 Slack 웹훅',
                'verbose_name_plural': 'Story 관전을 위한 Slack 웹훅',
            },
        ),
    ]
