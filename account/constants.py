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
    USERNAME_LENGTH_INVALID = ('username-length-invalid', '아이디는 {}자 이상 {}자 이하로 입력해주세요.')
    USERNAME_REG_EXP_INVALID = ('username-reg-exp-invalid', '아이디는 영문, 숫자만 입력 가능합니다.')
    NICKNAME_EXISTS = ('already-exists-nickname', '이미 사용중인 닉네임입니다.')
    NICKNAME_LENGTH_INVALID = ('nickname-length-invalid', '닉네임은 {}자 이상 {}자 이하로 입력해주세요.')
    NICKNAME_REG_EXP_INVALID = ('nickname-reg-exp-invalid', '닉네임은 한글, 영문, 숫자만 입력 가능합니다.')
    EMAIL_EXISTS = ('already-exists-email', '이미 가입한 이메일입니다.')
    CHECK_PASSWORD = ('check-password', '비밀번호와 비밀번호 확인이 동일하지 않습니다.')
    PASSWORD_LENGTH_INVALID = ('password-length-invalid', '비밀번호는 {}자 이상 {}자 이하로 입력해주세요.')
    EMAIL_REG_EXP_INVALID = ('email-reg-exp-invalid', '이메일 형식이 올바르지 않습니다.')


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


class UserStatusEnum(IntValueSelector):
    """
    데이터베이스에 1, 2, 3, 4 로 UserStatus 와 의미가 같아야 합니다.
    """
    NORMAL_USER = (1, '정상')
    LEAVE_USER = (2, '탈퇴')
    BLACK_USER = (3, '정지')
    DORMANT_USER = (4, '휴면')


SIGNUP_MACRO_VALIDATION_KEY = '{}:signup:count'
SIGNUP_MACRO_COUNT = 30
SIGNUP_MACRO_EXPIRE_SECONDS = 60 * 60 * 24

USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 16

NICKNAME_MIN_LENGTH = 2
NICKNAME_MAX_LENGTH = 8

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 30
