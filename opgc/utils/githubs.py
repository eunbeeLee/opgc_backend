import json
from dataclasses import dataclass, asdict
from datetime import datetime

import requests
from django.conf import settings
from furl import furl
from sentry_sdk import capture_exception

from apps.githubs.models import GithubUser
from utils.exceptions import GitHubUserDoesNotExist, RateLimit, manage_api_call_fail, insert_queue
from utils.organization import OrganizationService
from utils.repository import RepositoryService
from utils.slack import slack_notify_new_user

FURL = furl('https://api.github.com/')
GITHUB_RATE_LIMIT_URL = 'https://api.github.com/rate_limit'
CHECK_RATE_REMAIN = 100
USER_UPDATE_FIELDS = ['avatar_url', 'company', 'bio', 'blog', 'public_repos', 'followers', 'following',
                      'name', 'email', 'location']

"""
    * Authorization - access token 이 있는경우 1시간에 5000번 api 호출 가능 없으면 60번
"""


@dataclass
class UserInformationDto:
    name: str # 이름
    email: str # 이메일
    location: str # 국가
    avatar_url: str # 프로필 URL
    company: str # 회사
    bio: str # 설명
    blog: str # 블로그
    public_repos: int
    followers: int
    following: int
    repos_url: str
    organizations_url: str

    def __init__(self, name: str, email: str, location: str, avatar_url: str, company: str, bio: str,
                 blog: str, public_repos: int, followers: int, following: int, repos_url: str,
                 organizations_url: str):
        self.name = name
        self.email = email
        self.location = location
        self.avatar_url = avatar_url
        self.company = company
        self.bio = bio
        self.blog = blog
        self.public_repos = public_repos
        self.followers = followers
        self.following = following
        self.repos_url = repos_url
        self.organizations_url = organizations_url


class GithubInformationService(object):
    github_user = None

    def __init__(self, username, is_30_min_script=False):
        self.username = username
        self.new_repository_list = [] # 새로 생성될 레포지토리 리스트
        self.update_language_dict = {} # 업데이트할 language
        self.is_30_min_script = is_30_min_script

    def create_dto(self, user_information_data: dict) -> UserInformationDto:
        return UserInformationDto(
            name=user_information_data.get('name'),
            email=user_information_data.get('email'),
            location=user_information_data.get('location'),
            avatar_url=user_information_data.get('avatar_url'),
            company=user_information_data.get('company'),
            bio=user_information_data.get('bio'),
            blog=user_information_data.get('blog'),
            public_repos=user_information_data.get('public_repos'),
            followers=user_information_data.get('followers'),
            following=user_information_data.get('following'),
            repos_url=user_information_data.get('repos_url'),
            organizations_url=user_information_data.get('organizations_url')
        )

    def check_github_user(self) -> UserInformationDto:
        """
            Github User 정보를 가져오거나 생성하는 함수
        """
        user_api = FURL.set(path=f'/users/{self.username}').url
        res = requests.get(user_api, headers=settings.GITHUB_API_HEADER)

        if res.status_code == 404:
            raise GitHubUserDoesNotExist()
        elif res.status_code != 200:
            manage_api_call_fail(self.github_user, res.status_code)

        return self.create_dto(json.loads(res.content))

    def get_or_create_github_user(self, user_information: UserInformationDto) -> GithubUser:
        try:
            update_fields = ['status']
            github_user = GithubUser.objects.filter(username=self.username).get()
            github_user.status = GithubUser.UPDATING

            for key, value in asdict(user_information).items():
                if key in USER_UPDATE_FIELDS:
                    if getattr(github_user, key, '') != value:
                        setattr(github_user, key, value)
                        update_fields.append(key)

            github_user.save(update_fields=update_fields)

        except GithubUser.DoesNotExist:
            github_user = GithubUser.objects.create(
                username=self.username,
                name=user_information.name,
                email=user_information.email,
                location=user_information.location,
                avatar_url=user_information.avatar_url,
                company=user_information.company,
                bio=user_information.bio,
                blog=user_information.blog,
                public_repos=user_information.public_repos,
                followers=user_information.followers,
                following=user_information.following
            )
            slack_notify_new_user(github_user)

        return github_user

    def check_rete_limit(self) -> int:
        # 현재 호출할 수 있는 rate 체크 (token 있는경우 1시간당 5000번 없으면 60번 호출)
        res = requests.get(GITHUB_RATE_LIMIT_URL, headers=settings.GITHUB_API_HEADER)

        if res.status_code != 200:
            # 이 경우는 rate_limit api 가 호출이 안되는건데,
            # 이런경우가 깃헙장애 or rate_limit 호출에 제한이 있는지 모르겟다.
            if not self.is_30_min_script:
                insert_queue(self.username)
            capture_exception(Exception("Can't get RATE LIMIT."))

        """
            참고: https://docs.gitlab.com/ee/user/admin_area/settings/user_and_ip_rate_limits.html#response-headers
        """
        # 왠만하면 100 이상 호출하는 경우가 있어서 100으로 지정
        try:
            content = json.loads(res.content)
            remaining = content['rate']['remaining']
            if remaining < CHECK_RATE_REMAIN:
                if not self.is_30_min_script:
                    insert_queue(self.username)
                raise RateLimit()
        except json.JSONDecodeError:
            return 0

        return remaining

    def update_success(self, total_contribution: int, total_stargazers_count: int) -> GithubUser:
        """
            업데이트 성공 처리
        """
        self.github_user.status = GithubUser.COMPLETED
        self.github_user.updated = datetime.now()
        self.github_user.total_contribution = total_contribution
        self.github_user.total_stargazers_count = total_stargazers_count
        self.github_user.save(update_fields=['status', 'updated', 'total_contribution', 'total_stargazers_count'])

        return self.github_user

    def update(self):
        # 0. Github API 호출 가능한지 체크
        self.check_rete_limit()

        # 실제로 github에 존재하는 user인지 체크
        user_information: UserInformationDto = self.check_github_user()

        # 1. GithubUser 가 있는지 체크, 없으면 생성
        self.github_user: GithubUser = self.get_or_create_github_user(user_information)

        # 2. User의 repository 정보를 가져온다
        repo_res = requests.get(user_information.repos_url, headers=settings.GITHUB_API_HEADER)
        repo_service = RepositoryService(github_user=self.github_user)
        try:
            for repository_data in json.loads(repo_res.content):
                repository_dto = repo_service.create_dto(repository_data)
                repo_service.repositories.append(repository_dto)
        except json.JSONDecodeError:
            pass

        # 3. Organization 정보와 연관된 repository 업데이트
        org_service = OrganizationService(github_user=self.github_user)
        org_service.update_organization(user_information.organizations_url)
        org_service.get_organization_repository()

        # 4. Repository 정보 업데이트
        repo_service.repositories += org_service.repositories
        repo_service.update_repositories()

        # 5. Language and UserLanguage 업데이트
        repo_service.update_or_create_language()

        return self.update_success(
            total_contribution=repo_service.total_contribution,
            total_stargazers_count=repo_service.total_stargazers_count
        )
