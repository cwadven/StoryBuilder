import os
import json
from django.core.management.base import BaseCommand
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def create_file_from_project_root(path):
    if is_creatable_file(path):
        f = open(os.path.join(BASE_DIR, *path.split("/")), "w+")
        f.close()
    else:
        print("파일을 생성할 위치의 상위 폴더가 존재하지 않습니다.")


def create_folder_from_project_root(path):
    os.makedirs(os.path.join(BASE_DIR, *path.split("/")), exist_ok=True)


def is_creatable_file(path):
    has_parent_folder = len(path.split("/")) > 1
    is_parent_folder_exist = has_parent_folder and os.path.exists(os.path.join(BASE_DIR, *path.split("/")[:-1]))

    return (not has_parent_folder) or is_parent_folder_exist


def set_gitaction_settings(path, name, **kwargs):
    """
    CI/CD 용 yml 설정
    path - setting 할 yml 경로
    name - CI/CD 명
    kwargs - name: yml 이름 / branch: 적용 브랜치 / steps: 단계별 실행할 이름과 명령

    :param path: file-path
    :param name: CI/CD 명
    :param kwargs: branch-str, status-str, steps-list in objects [{"name": "", "run": ""}, ]
    :return:
    """
    if is_creatable_file(path):
        with open(path, 'w+') as f:
            f.writelines(f"name: {name}\n\n")

            f.writelines("on:\n")
            f.writelines(f"  {kwargs.get('status', 'push')}:\n")
            f.writelines(f"    branch: [ {kwargs.get('branch', 'master')} ]\n\n")

            f.writelines("jobs:\n")
            f.writelines("  build:\n")
            f.writelines("    runs-on: self-hosted\n\n")

            f.writelines("    steps:\n")

            if kwargs.get('steps'):
                for step in kwargs.get('steps'):
                    f.writelines("    - name: {step.get('name', '')}\n")
                    f.writelines("      run: |\n")
                    f.writelines("        {step.get('run', '')}\n\n")


class Command(BaseCommand):
    help = "GitActions 추가하는 명령"

    def add_arguments(self, parser):
        # 위치 인자
        parser.add_argument("github_action_file_name", type=str, help="GitHubAction 이름 설정")

        # 키워드 인자 (named arguments)
        parser.add_argument('-n', '--name', type=str, help='yml 안의 이름', default="CI/CD")
        parser.add_argument('-b', '--branch', type=str, help='어느 branch 에 적용할 지', default="master")
        parser.add_argument('-s', '--status', type=str, help='어느 상태에 할지 (ex.push)', default="push")
        parser.add_argument('-p', '--steps', type=str, help='어느 과정을 걸친 것인지, (ex. "[{"name": "aaa", "run": "bbb"}, {"name": "bbb", "run": "ccc"}]")', default="[]")

    def handle(self, *args, **kwargs):
        """
        실행할 동작을 정의해 줌
        """
        github_action_file_name = kwargs.get("github_action_file_name")
        branch = kwargs.get("branch")
        status = kwargs.get("status")
        name = kwargs.get("name")
        steps = kwargs.get("steps")

        try:
            steps = json.loads(steps)
            create_folder_from_project_root(".github/workflows")
            create_file_from_project_root(f".github/workflows/{github_action_file_name}.yml")
            set_gitaction_settings(
                f".github/workflows/{github_action_file_name}.yml",
                name,
                branch=branch,
                status=status,
                steps=steps
            )
            self.stdout.write(self.style.SUCCESS("GitActions Code Set"))
        except ValueError:
            self.stdout.write(self.style.ERROR("""
            steps 설정이 잘못되었습니다. (ex. "[{"name": "aaa", "run": "bbb"}, {"name": "bbb", "run": "ccc"}]")
            """))
