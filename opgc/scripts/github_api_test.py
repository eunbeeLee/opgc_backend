"""
    Github api 테스트 스크립트
    : 어떤 데이터들을 수집하고 가공할지 테스트
"""
import json

import requests


REPO = ''
USERNAME = ''
URL = 'https://api.github.com/'


def get_github_user_information():
    res = requests.get('')
    print(res)


def get_github_repo_languages():
    res = requests.get(f'{URL}repos/{USERNAME}/{REPO}/languages')
    print(json.loads(res.content.decode("UTF-8")))


def run():
    # get_github_repo_languages()
    get_github_repo_languages()
