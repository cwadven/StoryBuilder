from common_library import send_email
from config.celery import app


@app.task
def send_user_sheet_solved_email(user_sheet_answer_solve_id: int, emails: list) -> None:
    from story.models import UserSheetAnswerSolve
    try:
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.select_related(
            'user',
            'story',
            'sheet',
            'next_sheet_path__answer',
        ).get(id=user_sheet_answer_solve_id)
        send_email(
            title=f'[문제 해결] {user_sheet_answer_solve.user.username} 님이 {user_sheet_answer_solve.sheet_id}번 sheet 문제를 해결했습니다.',
            html_body_content='email/story/story_solved.html',
            payload={
                'story_id': user_sheet_answer_solve.story_id,
                'story_title': user_sheet_answer_solve.story.title,
                'sheet_id': user_sheet_answer_solve.sheet_id,
                'sheet_title': user_sheet_answer_solve.sheet.title,
                'username': user_sheet_answer_solve.user.username,
                'user_answer': user_sheet_answer_solve.answer,
            },
            to=emails
        )
    except UserSheetAnswerSolve.DoesNotExist:
        pass
