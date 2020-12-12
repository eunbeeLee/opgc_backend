"""
    Github api 테스트 스크립트
    : 어떤 데이터들을 수집하고 가공할지 테스트

"""

import json

import requests
from furl import furl

from apps.githubs.models import GithubUser, Repository, Language, UserOrganization, Organization, GithubLanguage
from conf.settings.local import OPGC_TOKEN

USERNAME = 'JAY-Chan9yu'
FURL = furl('https://api.github.com/')

"""
    * Authorization - access token 이 있는경우 1시간에 5000번 api 호출 가능 없으면 60번
"""
headers = {'Authorization': f'token {OPGC_TOKEN}'}
user_api = FURL.set(path=f'/users/{USERNAME}')


def get_or_create_github_user():
    """
        USer 가져오거나 생성하는 함
    """
    res = requests.get(user_api, headers=headers)

    if res.status_code != 200:
        return False

    user_information = json.loads(res.content.decode("UTF-8"))

    try:
        github_user = GithubUser.objects.filter(username=USERNAME).get()

        github_user.company = user_information.get('company')
        github_user.bio = user_information.get('bio')
        github_user.blog = user_information.get('blog')
        github_user.public_repos = user_information.get('public_repos')
        github_user.followers = user_information.get('followers')
        github_user.following = user_information.get('following')

        github_user.save(update_fields=[
            'company', 'bio', 'blog', 'public_repos', 'followers', 'following']
        )

    except GithubUser.DoesNotExist:
        github_user = GithubUser.objects.create(
            username=USERNAME,
            profile_image=user_information.get('avatar_url'),
            company=user_information.get('company'),
            bio=user_information.get('bio'),
            blog=user_information.get('blog'),
            public_repos=user_information.get('public_repos'),
            followers=user_information.get('followers'),
            following=user_information.get('following')
        )

    # 업데이트전 language number, total contribution of User 리셋
    github_user.total_contribution = 0
    github_user.save(update_fields=['total_contribution'])
    GithubLanguage.objects.filter(github_user=github_user).update(number=0)

    repo_res = requests.get(user_information.get('repos_url'), headers=headers)
    if repo_res.status_code != 200:
        return False

    repositories = json.loads(repo_res.content.decode("UTF-8"))
    update_repositories(github_user, repositories)
    update_organization(github_user, user_information.get('organizations_url'))


def update_repositories(user: GithubUser, repositories: dict):
    """
        레포지토리 업데이트 함수
    """
    total_contribution = 0
    for repository in repositories:
        _contribution = update_repo(user, repository)
        total_contribution += _contribution

    user.total_contribution += total_contribution
    user.save(update_fields=['total_contribution'])


def update_repo(user: GithubUser, repository: dict):
    _contribution = 0
    if repository.get('fork') is False:
        res = requests.get(repository.get('contributors_url'), headers=headers)

        if res.status_code != 200:
            return False

        for contributor in json.loads(res.content.decode("UTF-8")):
            # User 타입이고 contributor 가 본인인 경우
            if contributor.get('type') == 'User' and \
                    contributor.get('login') == user.username:
                _contribution += contributor.get('contributions')

                try:
                    repo = Repository.objects.filter(
                        github_user=user,
                        name=repository.get('name'),
                        full_name=repository.get('full_name'),
                        owner=repository.get('owner')['login'],
                    ).get()
                except Repository.DoesNotExist:
                    repo = Repository.objects.create(
                        github_user=user,
                        name=repository.get('name'),
                        full_name=repository.get('full_name'),
                        owner=repository.get('owner')['login'],
                        contribution=repository.get('contribution', 0)
                    )

                repo.contribution = _contribution
                repo.save(update_fields=['contribution'])

        update_language(user, repository.get('languages_url'))

    return _contribution


def get_language(language: str) -> Language:
    """
        프로그램 언어 가져오거나 생성하는 함수
    """

    try:
        language = Language.objects.filter(type=language).get()
    except Language.DoesNotExist:
        language = Language.objects.create(type=language)

    return language


def update_language(user: GithubUser, languages_url: str):
    res = requests.get(languages_url, headers=headers)

    if res.status_code != 200:
        return False

    languages_data = json.loads(res.content.decode("UTF-8"))
    for language_data in languages_data.items():
        language = get_language(language_data[0])

        try:
            github_language = GithubLanguage.objects.filter(
                language=language,
                github_user=user
            ).get()
        except GithubLanguage.DoesNotExist:
            github_language = GithubLanguage.objects.create(
                language=language,
                github_user=user
            )

        github_language.number += language_data[1]
        github_language.save(update_fields=['number'])


def update_organization(user: GithubUser, organization_url: str):
    """
        organization(소속) 업데이트 함
    """

    res = requests.get(organization_url, headers=headers)

    if res.status_code != 200:
        return False

    for organization_data in json.loads(res.content.decode("UTF-8")):
        try:
            organization = Organization.objects.filter(
                name=organization_data.get('login')
            ).get()

            organization.description = organization_data.get('description')
            organization.logo = organization_data.get('avatar_url')
            organization.save(update_fields=['logo', 'description'])

        except Organization.DoesNotExist:
            organization = Organization.objects.create(
                name=organization_data.get('login'),
                description=organization_data.get('description'),
                logo=organization_data.get('avatar_url'),
            )

        if not UserOrganization.objects.filter(
                github_user=user, organization=organization.id).exists():
            UserOrganization.objects.create(
                github_user=user,
                organization=organization
            )

        res = requests.get(organization_data.get('repos_url'), headers=headers)
        if res.status_code != 200:
            return False

        for repository in json.loads(res.content.decode("UTF-8")):
            res = requests.get(repository.get('contributors_url'), headers=headers)

            if res.status_code != 200:
                return False

            is_contributor = False
            for contributor in json.loads(res.content.decode("UTF-8")):
                if user.username == contributor.get('login'):
                    is_contributor = True
                    break

            if is_contributor:
                contribution = update_repo(user, repository)
                user.total_contribution += contribution
                user.save(update_fields=['total_contribution'])
                update_language(user, repository.get('languages_url'))


def run():
    get_or_create_github_user()
