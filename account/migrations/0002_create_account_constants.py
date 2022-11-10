from django.db import migrations


def forward(apps, schema_editor):
    UserProvider = apps.get_model('account', 'UserProvider')
    UserStatus = apps.get_model('account', 'UserStatus')
    UserType = apps.get_model('account', 'UserType')

    # 회원가입 유형
    UserProvider.objects.create(
        id=1,
        name='email',
        description='original user'
    )
    UserProvider.objects.create(
        id=2,
        name='kakao',
        description='social login by kakao.'
    )
    UserProvider.objects.create(
        id=3,
        name='naver',
        description='social login by naver.'
    )
    UserProvider.objects.create(
        id=4,
        name='google',
        description='social login by google.'
    )

    # 회원 상태
    UserStatus.objects.create(
        id=1,
        name='정상',
        description='정상적인 유저'
    )
    UserStatus.objects.create(
        id=2,
        name='탈퇴',
        description='탈퇴한 유저'
    )
    UserStatus.objects.create(
        id=3,
        name='정지',
        description='정지된 유저'
    )
    UserStatus.objects.create(
        id=4,
        name='휴면',
        description='휴면상태인 유저 3개월 간 로그인 하지 않은 경우'
    )

    # 회원 권한
    UserType.objects.create(
        id=1,
        name='관리자',
        description='관리자 입니다. (모든 권한을 가지고 있습니다.)'
    )
    UserType.objects.create(
        id=2,
        name='운영자',
        description='운영자 입니다. (다른 사람의 글을 삭제 할 수 있는 권한을 가지고 있습니다.)'
    )
    UserType.objects.create(
        id=3,
        name='일반',
        description='일반 사용자 입니다.'
    )


def backward(apps, schema_editor):
    UserProvider = apps.get_model('account', 'UserProvider')
    UserStatus = apps.get_model('account', 'UserStatus')
    UserType = apps.get_model('account', 'UserType')

    # 회원가입 유형
    UserProvider.objects.filter(
        id__in=[1, 2, 3, 4]
    ).delete()

    # 회원 상태
    UserStatus.objects.filter(
        id__in=[1, 2, 3, 4]
    ).delete()

    # 회원 권한
    UserType.objects.filter(
        id__in=[1, 2, 3]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
