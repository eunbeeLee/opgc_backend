"""
    업데이트 한지 7일이 지난 유저들 업데이트 배치 스크립트
    : 일단 유저 적을때는 매일 새벽에 돌리도록(3,4,5)
"""
import concurrent.futures
import timeit
from datetime import datetime, timedelta

from chunkator import chunkator
from sentry_sdk import capture_exception

from apps.githubs.models import GithubUser
from utils.exceptions import RateLimit
from utils.githubs import GithubInformationService
from utils.slack import slack_notify_update_fail, slack_update_older_week_user


def run():
    # 1. 스크립트를 시작하기전 rate_limit 를 체크한다.
    try:
        rate_limit_check_service = GithubInformationService(None)
        rate_limit_check_service.check_rete_limit()
    except RateLimit:
        return

    older_week_date = datetime.now() - timedelta(7)
    github_user_qs = GithubUser.objects.filter(updated__lte=older_week_date)
    if not github_user_qs:
        return

    start_time = timeit.default_timer()  # 시작 시간 체크
    slack_update_older_week_user(status='시작', message='')

    update_user_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for github_user in chunkator(github_user_qs, 1000):
            try:
                github_information_service = GithubInformationService(github_user.username)
                executor.submit(github_information_service.update)
                update_user_count += 1

            except RateLimit:
                slack_notify_update_fail(
                    message=f'Rate Limit 로 인해 업데이트가 실패되었습니다. {update_user_count}명만 업데이트 되었습니다.😭'
                )
                # rate limit면 다른 유저들도 업데이드 못함
                return

            except Exception as e:
                capture_exception(e)

    terminate_time = timeit.default_timer()  # 종료 시간 체크
    slack_update_older_week_user(
        status='완료',
        message=f'업데이트가 {terminate_time - start_time}초 걸렸습니다. 🤩',
        update_user=update_user_count
    )
