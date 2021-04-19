"""
    1일 1커밋 크롤링으로 업데이트
"""
import concurrent.futures
import timeit

import requests
from bs4 import BeautifulSoup

from chunkator import chunkator
from sentry_sdk import capture_exception

from apps.githubs.models import GithubUser
from utils.slack import slack_update_1day_1commit


def check_1day_1commit(user_id: int, username: str):
    source = requests.get(f'https://github.com/{username}').text
    soup = BeautifulSoup(source, "lxml") # html.parse 보다 lxml이 더 빠르다고 한다
    count = 0

    for rect in reversed(soup.select('rect')):
        if rect.get('data-count') is None:
            continue

        if rect.get('data-count') == '0':
            break
        count += 1

    # print(f'{username}: {count}')
    GithubUser.objects.filter(id=user_id).update(continuous_commit_day=count)


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크
    slack_update_1day_1commit(status='시작🌱', message='')

    github_users = GithubUser.objects.all()
    user_count = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for github_user in chunkator(github_users, 1000):
            try:
                executor.submit(check_1day_1commit, github_user.id, github_user.username)
                user_count += 1
            except Exception as e:
                # 멀티 프로세싱을 많이 안써봐서 어떤 예외가 나올지 몰라 리포팅
                capture_exception(e)

    terminate_time = timeit.default_timer()  # 종료 시간 체크
    slack_update_1day_1commit(
        status='완료🌿',
        message=f'1일 1커밋 카운트 업데이트가 {terminate_time - start_time}초 걸렸습니다.😎 (총 {user_count}명)',
    )
