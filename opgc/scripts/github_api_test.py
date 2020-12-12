"""
    Github api 테스트 스크립트
    : 어떤 데이터들을 수집하고 가공할지 테스트
"""
import json

import requests
from furl import furl

from apps.githubs.models import GithubUser

REPO = ''
USERNAME = 'JAY-Chan9yu'
FURL = furl('https://api.github.com/')

user_api = FURL.set(path=f'/users/{USERNAME}')


def get_or_create_github_user():
    res = requests.get(user_api)

    if res.status_code != 200:
        return False

    user_information = json.loads(res.content.decode("UTF-8"))

    try:
        github_user = GithubUser.objects.filter(username=USERNAME).get()
    except GithubUser.DoesNotExist:
        github_user = GithubUser.objects.create(
            username=USERNAME,
            profile_image=user_information.get('avatar_url')
        )

    print(github_user)


def run():
    get_or_create_github_user()
