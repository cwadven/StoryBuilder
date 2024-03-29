# Generated by Django 3.2.16 on 2023-04-23 18:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0020_sheetanswer_is_always_correct'),
    ]

    operations = [
        migrations.CreateModel(
            name='WrongAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=100, verbose_name='틀린 답')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('sheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='story.sheet')),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='story.story')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '틀린 답',
                'verbose_name_plural': '틀린 답',
            },
        ),
    ]
