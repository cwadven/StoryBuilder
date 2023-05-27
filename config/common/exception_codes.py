from rest_framework.exceptions import APIException


class PageSizeMaximumException(APIException):
    status_code = 400
    default_detail = '사이즈를 초과했습니다.'
    default_code = 'page-size-maximum'


class LoginFailedException(APIException):
    status_code = 400
    default_detail = '로그인에 실패했습니다.'
    default_code = 'login-error'


class SocialLoginTokenErrorException(APIException):
    status_code = 400
    default_detail = '소셜 로그인에 발급된 토큰에 문제가 있습니다.'
    default_code = 'social-token-error'


class BlackUserException(APIException):
    status_code = 400
    default_detail = '정지된 유저입니다.'
    default_code = 'inaccessible-user-login'


class DormantUserException(APIException):
    status_code = 400
    default_detail = '휴면상태의 유저입니다.'
    default_code = 'dormant-user-login'


class LeaveUserException(APIException):
    status_code = 400
    default_detail = '탈퇴상태의 유저입니다.'
    default_code = 'leave-user-login'


class UnknownPlatformException(APIException):
    status_code = 400
    default_detail = '알 수 없는 로그인 방식입니다.'
    default_code = 'platform-error'


class UnknownPlatformException(APIException):
    status_code = 400
    default_detail = '알 수 없는 로그인 방식입니다.'
    default_code = 'platform-error'


class MissingMandatoryParameterException(APIException):
    status_code = 400
    default_detail = '입력값을 다시 확인해주세요.'
    default_code = 'missing-mandatory-parameter'


class StoryDoesNotExists(APIException):
    status_code = 400
    default_detail = '스토리를 불러올 수 없습니다.'
    default_code = 'story-does-not-exists'


class StartingSheetDoesNotExists(APIException):
    status_code = 400
    default_detail = '스토리를 불러올 수 없습니다.'
    default_code = 'starging-sheet-does-not-exists'


class SheetDoesNotExists(APIException):
    status_code = 400
    default_detail = '존재하지 않은 Sheet 입니다.'
    default_code = 'sheet-does-not-exists'


class SheetNotAccessibleException(APIException):
    status_code = 400
    default_detail = '접근할 수 없는 Sheet 입니다.'
    default_code = 'sheet-not-accessible'


class LoginRequiredException(APIException):
    status_code = 400
    default_detail = '로그인이 필요합니다.'
    default_code = 'login-require'


class CannotCreateUserException(APIException):
    status_code = 400

    def __init__(self, detail, code):
        super().__init__(detail, code)


class UserSheetHintHistoryAlreadyExists(APIException):
    status_code = 400
    default_detail = '이미 Sheet hint 를 받은 기록이 있습니다.'
    default_code = 'already-has-sheet-hint-history'


class SheetHintDoesNotExists(APIException):
    status_code = 400
    default_detail = '존재하지 않은 Sheet hint 입니다.'
    default_code = 'sheet-hint-does-not-exists'


class NotEnoughUserPoints(APIException):
    status_code = 400
    default_detail = '유저의 포인트가 부족합니다.'
    default_code = 'not-enough-user-points'


class BannerDoesNotExists(APIException):
    status_code = 400
    default_detail = '존재하지 않은 배너 입니다.'
    default_code = 'banner-does-not-exists'


class PointProductNotExists(APIException):
    status_code = 400
    default_detail = '유효하지 않은 포인트 상품 입니다.'
    default_code = '유효하지 않은 포인트 상품 입니다.'


class OrderNotExists(APIException):
    status_code = 400
    default_detail = '유효하지 주문 입니다.'
    default_code = '유효하지 주문 입니다.'
