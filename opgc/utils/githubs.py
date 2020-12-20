import json

import requests
from django.conf import settings
from furl import furl
from sentry_sdk import capture_exception

from apps.githubs.models import GithubUser, Repository, Language, UserOrganization, Organization, GithubLanguage

FURL = furl('https://api.github.com/')

"""
    * Authorization - access token 이 있는경우 1시간에 5000번 api 호출 가능 없으면 60번
"""


class UpdateGithubInformation(object):
    total_contribution = None

    def __init__(self, username):
        self.headers = {'Authorization': f'token {settings.OPGC_TOKEN}'}
        self.total_contribution = 0
        self.username = username

    def check_github_user(self):
        """
            Github User 정보를 가져오거나 생성하는 함수
        """
        user_api = FURL.set(path=f'/users/{self.username}').url
        res = requests.get(user_api, headers=self.headers)

        if res.status_code != 200:
            return False, res.status_code

        user_information = json.loads(res.content.decode("UTF-8"))

        return True, user_information

    def get_or_create_github_user(self, user_information: dict):
        try:
            github_user = GithubUser.objects.filter(username=self.username).get()
            github_user.status = GithubUser.UPDATING
            github_user.company = user_information.get('company')
            github_user.bio = user_information.get('bio')
            github_user.blog = user_information.get('blog')
            github_user.public_repos = user_information.get('public_repos')
            github_user.followers = user_information.get('followers')
            github_user.following = user_information.get('following')

            github_user.save(
                update_fields=['status', 'company', 'bio', 'blog', 'public_repos', 'followers', 'following']
            )

        except GithubUser.DoesNotExist:
            github_user = GithubUser.objects.create(
                username=self.username,
                profile_image=user_information.get('avatar_url'),
                company=user_information.get('company'),
                bio=user_information.get('bio'),
                blog=user_information.get('blog'),
                public_repos=user_information.get('public_repos'),
                followers=user_information.get('followers'),
                following=user_information.get('following')
            )

        # 업데이트전 language number, total contribution of User 리셋
        GithubLanguage.objects.filter(github_user=github_user).update(number=0)

        return github_user

    def update_repositories(self, user: GithubUser, repositories: str):
        """
            레포지토리 업데이트 함수
        """
        repo_res = requests.get(repositories, headers=self.headers)
        if repo_res.status_code != 200:
            return False

        res = json.loads(repo_res.content.decode("UTF-8"))

        total_contribution = 0
        for repository in res:
            _contribution = self.update_repo(user, repository)
            total_contribution += _contribution

        self.total_contribution += total_contribution

        return True

    def update_repo(self, user: GithubUser, repository: dict):
        _contribution = 0
        if repository.get('fork') is False:
            res = requests.get(repository.get('contributors_url'), headers=self.headers)

            if res.status_code != 200:
                # todo: log 남기기
                return 0

            for contributor in json.loads(res.content.decode("UTF-8")):
                # User 타입이고 contributor 가 본인인 경우
                if contributor.get('type') == 'User' and contributor.get('login') == user.username:
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

            self.update_language(user, repository.get('languages_url'))

        return _contribution

    def get_language(self, language: str) -> Language:
        """
            프로그램 언어 가져오거나 생성하는 함수
        """

        try:
            language = Language.objects.filter(type=language).get()
        except Language.DoesNotExist:
            language = Language.objects.create(type=language)

        return language

    def update_language(self, user: GithubUser, languages_url: str):
        """
            repository 에서 사용중인 언어를 찾아서 User 의 사용언엉로 추가
        """
        res = requests.get(languages_url, headers=self.headers)
        if res.status_code != 200:
            return False

        languages_data = json.loads(res.content.decode("UTF-8"))
        for language_data in languages_data.items():
            language = self.get_language(language_data[0])

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

        return True

    def update_organization(self, user: GithubUser, organization_url: str) -> bool:
        """
            organization(소속) 업데이트 함
        """

        res = requests.get(organization_url, headers=self.headers)
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

            if not UserOrganization.objects.filter(github_user=user, organization=organization.id).exists():
                UserOrganization.objects.create(
                    github_user=user,
                    organization=organization
                )

            ################################################################################
            #    organization 에 있는 repository 중 User 가 Contributor 인 repository 를 등록한다.
            ################################################################################
            res = requests.get(organization_data.get('repos_url'), headers=self.headers)
            if res.status_code != 200:
                return False

            for repository in json.loads(res.content.decode("UTF-8")):
                res = requests.get(repository.get('contributors_url'), headers=self.headers)

                if res.status_code != 200:
                    return False

                for contributor in json.loads(res.content.decode("UTF-8")):
                    if user.username == contributor.get('login'):
                        contribution = self.update_repo(user, repository)
                        self.total_contribution += contribution
                        self.update_language(user, repository.get('languages_url'))
                        break

        return True

    def update(self, user_information: dict):
        github_user = None

        try:
            # 1. GithubUser 가 있는지 체크, 없으면 생성
            github_data = self.get_or_create_github_user(user_information)
            if not github_data:
                return False
            github_user = github_data

            # 2. Repository 정보 업데이트
            is_update_repo = self.update_repositories(github_user, user_information.get('repos_url'))
            if not is_update_repo:
                github_user.status = GithubUser.FAIL
                github_user.save(update_fields=['status'])
                return False

            # 3. Organization 정보와 연관된 repository 업데이트
            is_update_org = self.update_organization(github_user, user_information.get('organizations_url'))
            if not is_update_org:
                github_user.status = GithubUser.FAIL
                github_user.save(update_fields=['status'])
                return False

        except Exception as e:
            capture_exception(e)
            if github_user:
                github_user.status = GithubUser.COMPLETED
                github_user.save(update_fields=['status'])

            return False

        github_user.status = GithubUser.COMPLETED
        github_user.total_contribution = self.total_contribution
        github_user.save(update_fields=['status', 'total_contribution'])
        return github_user
