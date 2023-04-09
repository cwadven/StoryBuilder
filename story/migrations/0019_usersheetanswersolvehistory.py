# Generated by Django 3.2.16 on 2023-04-09 12:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0018_storyslacksubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSheetAnswerSolveHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet_question', models.TextField(null=True)),
                ('answer', models.TextField(null=True)),
                ('solved_sheet_version', models.IntegerField(null=True)),
                ('solved_answer_version', models.IntegerField(null=True)),
                ('solving_status', models.CharField(choices=[('solving', '진행중'), ('solved', '성공')], db_index=True, default='solving', max_length=20)),
                ('start_time', models.DateTimeField(null=True)),
                ('solved_time', models.DateTimeField(null=True)),
                ('group_id', models.IntegerField(blank=True, db_index=True, help_text='한 싸이클에 대한 UserSheetAnswerSolve 를 구분하기 위한 id', null=True)),
                ('next_sheet_path', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.nextsheetpath')),
                ('sheet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.sheet')),
                ('solved_sheet_answer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.sheetanswer')),
                ('story', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.story')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user_story_solve', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.userstorysolve')),
            ],
            options={
                'verbose_name': '유저 풀이 히스토리',
                'verbose_name_plural': '유저 풀이 히스토리',
            },
        ),
    ]
