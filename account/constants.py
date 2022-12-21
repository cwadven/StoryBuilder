from account.helpers.social_login_helpers import KakaoSocialType, NaverSocialType, GoogleSocialType
from config.common.enums import IntValueSelector, StrValueLabel
from config.common.exception_codes import LeaveUserException, BlackUserException, DormantUserException, \
    UnknownPlatformException


class SocialTypeSelector(IntValueSelector):
    """
    데이터베이스에 2, 3, 4 로 UserProvider 와 의미가 같아야 합니다.
    """
    KAKAO_SOCIAL_TYPE = (2, KakaoSocialType)
    NAVER_SOCIAL_TYPE = (3, NaverSocialType)
    GOOGLE_SOCIAL_TYPE = (4, GoogleSocialType)

    @classmethod
    def _missing_(cls, value):
        raise UnknownPlatformException()


class UserStatusExceptionTypeSelector(IntValueSelector):
    """
    데이터베이스에 2, 3, 4 로 UserStatus 와 의미가 같아야 합니다.
    """
    LEAVE_USER_EXCEPTION = (2, LeaveUserException)
    BLACK_USER_EXCEPTION = (3, BlackUserException)
    DORMANT_USER_EXCEPTION = (4, DormantUserException)


class UserCreationExceptionMessage(StrValueLabel):
    USERNAME_EXISTS = ('already-exists-username', '이미 사용중인 아이디입니다.')
    NICKNAME_EXISTS = ('already-exists-nickname', '이미 사용중인 닉네임입니다.')


class UserProviderEnum(IntValueSelector):
    """
    상수 값으로 User Provider 제어하기
    """
    EMAIL = (1, 'email')
    KAKAO = (2, 'kakao')
    NAVER = (3, 'naver')
    GOOGLE = (4, 'google')


class UserTypeEnum(IntValueSelector):
    """
    상수 값으로 User Type 제어하기
    """
    SYSTEM_ADMIN = (1, '관리자')
    PRODUCT_ADMIN = (2, '운영자')
    NORMAL_USER = (3, '일반')
