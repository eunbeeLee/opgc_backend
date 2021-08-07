import time
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import Response
from sentry_sdk import capture_exception


def retry_handle(username, year) -> Optional[Response]:
    # todo: 공통 util 로 분리
    retry_cnt = 0
    res = None

    while retry_cnt < 5:
        res = requests.get(f'https://github.com/users/{username}/contributions?to={year}-12-31')

        if res.status_code != 200:
            retry_cnt += 1
            print(f'retry {retry_cnt}')
            continue

        break

    if retry_cnt >= 5:
        capture_exception(Exception(f'Requests Retry Limit - {username}'))

    return res


def get_continuous_commit_day(username: str) -> (bool, int):
    time.sleep(0.1)  # 429 에러 때문에 약간의 sleep 을 준다.

    now = datetime.now() - timedelta(days=1)  # 업데이트 당일 전날부터 체크
    continuous_count = 0
    is_commit_aborted = False  # 1일 1커밋이 중단 됐는지
    is_completed = True  # 크롤링이 정상적으로 완료 되었는지

    for year in range(now.year, 2007, -1):  # 2007년에 깃허브 오픈
        res = retry_handle(username, year)

        if not res:
            is_completed = False
            break

        soup = BeautifulSoup(res.text, "lxml")  # html.parse 보다 lxml이 더 빠르다고 한다
        for rect in reversed(soup.select('rect')):
            if not rect.get('data-date') or now.date() < datetime.strptime(rect.get('data-date'), '%Y-%m-%d').date():
                continue

            if not rect.get('data-count') or rect.get('data-count') == '0':
                is_commit_aborted = True
                break

            continuous_count += 1

        if is_commit_aborted:
            break

    return is_completed, continuous_count
