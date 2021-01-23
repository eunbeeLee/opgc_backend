"""
    30분마다 실행되는 Github user 업데이트
    : github api가 rate_limit 걸려서 더이상 호출하지 못하는 경우

"""
import timeit

from chunkator import chunkator

from apps.reservations.models import UpdateUserQueue
from utils.githubs import UpdateGithubInformation
from utils.slack import slack_update_github_user, slack_notify_update_fail


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크

    update_user_queue_qs = UpdateUserQueue.objects.filter(
        status__in=[UpdateUserQueue.READY, UpdateUserQueue.FAIL]
    )

    slack_update_github_user(status='시작', message='')
    update_user_count = 0
    for user_queue in chunkator(update_user_queue_qs, 1000):
        update_github_information = UpdateGithubInformation(user_queue.username, True)
        update_github_information.update()

        # rate_limit로 api호출 불가능한 상황
        if update_github_information.fail_status_code == 403:
            user_queue.status = UpdateUserQueue.FAIL
            user_queue.save(update_fields=['status'])
            slack_notify_update_fail(
                message=f'Rate Limit 로 인해 업데이트가 실패되었습니다. {update_user_count}명만 업데이트 되었습니다.'
            )
            return

        user_queue.status = UpdateUserQueue.SUCCESS
        user_queue.save(update_fields=['status'])
        update_user_count += 1

    terminate_time = timeit.default_timer()  # 종료 시간 체크
    slack_update_github_user(
        status='완료',
        message=f'업데이트가 {terminate_time - start_time}초 걸렸습니다.',
        update_user=update_user_count
    )
