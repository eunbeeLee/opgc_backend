import asyncio
import datetime
import time
import timeit

import aiohttp
from bs4 import BeautifulSoup

from chunkator import chunkator

from apps.githubs.models import GithubUser
from utils.githubs import GithubInformationService
from utils.slack import slack_update_1day_1commit


async def check_1day_1commit(user_id: int, username: str):
    """
        1일 1커밋 크롤링으로 업데이트
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://github.com/{username}') as res:
            source = await res.text()
            soup = BeautifulSoup(source, "lxml")  # html.parse 보다 lxml이 더 빠르다고 한다
            count = 0

            now = datetime.datetime.now() - datetime.timedelta(days=1)
            for rect in reversed(soup.select('rect')):
                # 업데이트 당일 전날부터 체크
                if not rect.get('data-date') or \
                        now.date() < datetime.datetime.strptime(rect.get('data-date'), '%Y-%m-%d').date():
                    continue

                if rect.get('data-count') is None or rect.get('data-count') == '0':
                    break

                count += 1

    # print(f'{username}: {count}')
    tier = GithubInformationService.get_tier_statistics(count)
    GithubUser.objects.filter(id=user_id).update(continuous_commit_day=count, tier=tier)
    time.sleep(0.1)  # 429 에러 때문에 약간의 sleep 을 준다.


async def update_1day_1commit_futures():
    github_users = GithubUser.objects.all()

    futures = [asyncio.ensure_future(
        check_1day_1commit(github_user.id, github_user.username)) for github_user in chunkator(github_users, 1000)
    ]

    await asyncio.gather(*futures)


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크
    slack_update_1day_1commit(status='시작🌱', message='')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_1day_1commit_futures())

    terminate_time = timeit.default_timer()  # 종료 시간 체크
    slack_update_1day_1commit(
        status='완료🌿',
        message=f'1일 1커밋 카운트 업데이트가 {terminate_time - start_time}초 걸렸습니다.😎',
    )
