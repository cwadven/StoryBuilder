from common_library import optional_key, mandatory_key, paging
from config.common.exception_codes import LoginRequiredException


def optionals(*keys):
    def decorate(func):
        def wrapper(View, *args, **kwargs):
            optional = dict()
            for arg in keys:
                for key, val in arg.items():
                    data = optional_key(View.request, key, val)
                    optional[key] = data
            return func(View, o=optional, *args, **kwargs)

        return wrapper

    return decorate


def mandatories(*keys):
    def decorate(func):
        def wrapper(View, *args, **kwargs):
            mandatory = dict()
            for key in keys:
                data = mandatory_key(View.request, key)
                mandatory[key] = data
            return func(View, m=mandatory, *args, **kwargs)

        return wrapper

    return decorate


def pagination(default_size=10):
    def decorate(func):
        def wrapper(View, *args, **kwargs):
            start_row, end_row = paging(View.request, default_size)
            return func(View, start_row=start_row, end_row=end_row, *args, **kwargs)

        return wrapper

    return decorate


def custom_login_required_for_method(func):
    # TODO 테스트케이스 작성
    # TODO 메서드용이 아닌 클래스에 데코레이터, 함수에 데코레이터 용으로 분기처리 만들기
    def wrapper(*args, **kwargs):
        if not args[1].user.is_authenticated:
            raise LoginRequiredException()
        return func(*args, **kwargs)
    return wrapper
