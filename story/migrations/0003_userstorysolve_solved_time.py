# Generated by Django 3.2.14 on 2022-12-04 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0002_userstorysolve'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstorysolve',
            name='solved_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
