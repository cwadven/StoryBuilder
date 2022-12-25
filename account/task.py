from common_library import send_email
from config.celery import app


@app.task
def send_one_time_token_email(email: str, one_time_token: str) -> None:
    send_email(
        title='[회원가입] Story Solver 인증',
        html_body_content='email/account/one_time_token.html',
        payload={
            'body': '[인증번호]',
            'message': f'{one_time_token}'
        },
        to=[email]
    )
