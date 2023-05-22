# Generated by Django 3.2.16 on 2023-05-21 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PointProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=120, verbose_name='상품명')),
                ('description', models.TextField(blank=True, null=True, verbose_name='상품 설명')),
                ('image', models.TextField(blank=True, null=True, verbose_name='상품 이미지')),
                ('amount', models.IntegerField(db_index=True, verbose_name='가격 정보')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='활성화')),
                ('start_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='시작 시간')),
                ('end_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='끝 시간')),
                ('quantity', models.IntegerField(db_index=True, default=0, verbose_name='수량')),
                ('is_sold_out', models.BooleanField(db_index=True, default=False, verbose_name='품절 여부')),
                ('bought_count', models.BigIntegerField(db_index=True, default=0, verbose_name='구매 수')),
                ('review_count', models.BigIntegerField(db_index=True, default=0, verbose_name='리뷰 수')),
                ('review_rate', models.FloatField(db_index=True, default=0, verbose_name='리뷰 평점')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('point', models.IntegerField(db_index=True, verbose_name='포인트')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdditionalPointProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=120, verbose_name='추가 포인트 주는 이유')),
                ('point', models.IntegerField(verbose_name='추가 포인트')),
                ('start_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='유효한 시작 시간')),
                ('end_time', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='유효한 끝 시간')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('point_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.pointproduct')),
            ],
        ),
    ]