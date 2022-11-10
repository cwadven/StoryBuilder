from django.db import migrations
from datetime import datetime


def forward(apps, schema_editor):
    User = apps.get_model('account', 'User')
    user = User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin',
    )
    user.user_type_id = 1
    user.user_status_id = 1
    user.user_provider_id = 1
    user.first_name = '관'
    user.last_name = '리자'
    user.nickname = 'admin'
    user.last_login = datetime.now()
    user.save()


def backward(apps, schema_editor):
    User = apps.get_model('account', 'User')
    User.objects.filter(
        username='admin',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_create_account_constants'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
