# Generated by Django 3.2.16 on 2022-11-15 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NextSheetPath',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='가중치')),
            ],
        ),
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='제목')),
                ('question', models.TextField(verbose_name='질문')),
                ('image', models.TextField(blank=True, null=True, verbose_name='대표 이미지')),
                ('background_image', models.TextField(blank=True, null=True, verbose_name='대표 배경 이미지')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='삭제 여부')),
                ('version', models.IntegerField(default=0, verbose_name='수정 시 자동 변경 되는 버전')),
                ('is_start', models.BooleanField(default=False, verbose_name='시작 부분 여부')),
                ('is_final', models.BooleanField(default=False, verbose_name='마지막 부분 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='제목')),
                ('description', models.TextField(blank=True, null=True, verbose_name='설명')),
                ('image', models.TextField(blank=True, null=True, verbose_name='대표 이미지')),
                ('background_image', models.TextField(blank=True, null=True, verbose_name='대표 배경 이미지')),
                ('played_count', models.IntegerField(default=0, verbose_name='플레이 횟수')),
                ('view_count', models.IntegerField(default=0, verbose_name='조회 횟수')),
                ('review_rate', models.IntegerField(default=0, verbose_name='평점')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='삭제 여부')),
                ('displayable', models.BooleanField(default=True, verbose_name='활성화 여부')),
                ('playing_point', models.IntegerField(default=0, verbose_name='플레이를 위한 포인트')),
                ('need_to_pay', models.BooleanField(default=False, verbose_name='구매 여부')),
                ('free_to_play_sheet_count', models.IntegerField(default=0, verbose_name='무료로 즐길 수 있는 Sheet 갯수')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SheetAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(verbose_name='정답')),
                ('answer_reply', models.TextField(blank=True, null=True, verbose_name='정답 후 반응')),
                ('next_sheet_paths', models.ManyToManyField(blank=True, null=True, related_name='next_sheet_paths', through='story.NextSheetPath', to='story.Sheet', verbose_name='다음 Sheet 경로')),
                ('sheet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='story.sheet')),
            ],
        ),
        migrations.AddField(
            model_name='sheet',
            name='story',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.story'),
        ),
        migrations.AddField(
            model_name='nextsheetpath',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='story.sheetanswer'),
        ),
        migrations.AddField(
            model_name='nextsheetpath',
            name='sheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='story.sheet'),
        ),
    ]
