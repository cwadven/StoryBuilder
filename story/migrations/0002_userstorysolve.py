# Generated by Django 3.2.14 on 2022-12-04 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStorySolve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('solving', '진행중'), ('give_up', '포기'), ('solved', '성공')], default='solving', max_length=20)),
                ('story', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='story.story')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
