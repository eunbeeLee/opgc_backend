import asyncio
import time
import timeit
from datetime import timedelta, datetime

import aiohttp
from bs4 import BeautifulSoup

from chunkator import chunkator

from apps.githubs.models import GithubUser
from utils.slack import slack_update_1day_1commit


async def check_1day_1commit(github_user: GithubUser):
    """
        1일 1커밋 크롤링으로 업데이트
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://github.com/{github_user.username}') as res:
            source = await res.text()
            soup = BeautifulSoup(source, "lxml")  # html.parse 보다 lxml이 더 빠르다고 한다
            count = 0

            now = datetime.now() - timedelta(days=1)
            for rect in reversed(soup.select('rect')):
                # 업데이트 당일 전날부터 체크
                if not rect.get('data-date') or \
                        now.date() < datetime.strptime(rect.get('data-date'), '%Y-%m-%d').date():
                    continue

                if not rect.get('data-count') or rect.get('data-count') == '0':
                    break

                count += 1

    #print(f'{github_user.username}: {count}')
    github_user.continuous_commit_day = count
    github_user.save(update_fields=['continuous_commit_day'])
    time.sleep(0.1)  # 429 에러 때문에 약간의 sleep 을 준다.


def update_1day_1commit(github_user_id: int = None):
    async def update_1day_1commit_futures(user_id: int = None):
        github_users = GithubUser.objects.filter(id=user_id) if user_id else GithubUser.objects.all()

        if not github_users:
            return

        futures = [
            asyncio.ensure_future(check_1day_1commit(github_user)) for github_user in chunkator(github_users, 1000)
        ]

        await asyncio.gather(*futures)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_1day_1commit_futures(github_user_id))


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크
    slack_update_1day_1commit(status='시작🌱', message='')

    update_1day_1commit()

    terminate_time = timeit.default_timer()  # 종료 시간 체크
    slack_update_1day_1commit(
        status='완료🌿',
        message=f'1일 1커밋 카운트 업데이트가 {terminate_time - start_time:.2f}초 걸렸습니다.😎',
    )
