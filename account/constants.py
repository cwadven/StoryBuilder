from account.helpers.social_login_helpers import KakaoSocialType, NaverSocialType, GoogleSocialType
from config.common.enums import IntValueSelector
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
