import json
from datetime import datetime

import requests
from django.conf import settings
from furl import furl
from sentry_sdk import capture_exception

from apps.githubs.models import GithubUser, Repository, Language, UserOrganization, Organization, UserLanguage
from apps.reservations.models import UpdateUserQueue
from utils.slack import slack_notify_new_user, slack_notify_update_user_queue

FURL = furl('https://api.github.com/')
GITHUB_RATE_LIMIT_URL = 'https://api.github.com/rate_limit'
CHECK_RATE_REMAIN = 100

"""
    * Authorization - access token 이 있는경우 1시간에 5000번 api 호출 가능 없으면 60번
"""


class UpdateGithubInformation(object):

    def __init__(self, username, is_30_min_script=False):
        self.headers = {'Authorization': f'token {settings.OPGC_TOKEN}'}
        self.total_contribution = 0
        self.username = username
        self.new_organization_list = []
        self.repositories = [] # 업데이트할 레포지토리 리스트
        self.update_language_dict = {} # update 할 language
        self.fail_status_code = 0 # github_api fail status
        self.is_30_min_script = is_30_min_script

    def check_github_user(self) -> (bool, dict):
        """
            Github User 정보를 가져오거나 생성하는 함수
        """
        user_api = FURL.set(path=f'/users/{self.username}').url
        res = requests.get(user_api, headers=self.headers)

        if res.status_code != 200:
            self.fail_status_code = res.status_code
            return False, None

        user_information = json.loads(res.content.decode("UTF-8"))

        return True, user_information

    def get_or_create_github_user(self, user_information: dict):
        try:
            github_user = GithubUser.objects.filter(username=self.username).get()
            github_user.status = GithubUser.UPDATING
            github_user.company = user_information.get('company') or ''
            github_user.bio = user_information.get('bio') or ''
            github_user.blog = user_information.get('blog') or ''
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
                company=user_information.get('company') or '',
                bio=user_information.get('bio') or '',
                blog=user_information.get('blog') or '',
                public_repos=user_information.get('public_repos'),
                followers=user_information.get('followers'),
                following=user_information.get('following')
            )
            slack_notify_new_user(github_user)

        # 업데이트전 language number, total contribution of User 리셋
        UserLanguage.objects.filter(github_user=github_user).update(number=0)

        return github_user

    def update_repositories(self, user: GithubUser) -> bool:
        """
            레포지토리 업데이트 함수
        """
        new_repository_list = []
        total_contribution = 0

        # 유저의 현재 모든 repository를 가져온다.
        user_repositories = list(Repository.objects.filter(github_user=user))
        for repository in self.repositories:
            is_exist_repo = False

            for idx, repo in enumerate(user_repositories):
                if repo.full_name == repository.get('full_name') and repo.owner == repository.get('owner'):
                    is_exist_repo = True
                    user_repositories.pop(idx)

                    # repository update
                    if repo.contribution != repository.get('contribution'):
                        repo.contribution = repository.get('contribution')
                        repo.save(update_fields=['contribution'])
                    break

            # 새로운 레포지토리
            if not is_exist_repo:
                _contribution, new_repository = self.create_repository(user, repository)

                if new_repository:
                    new_repository_list.append(new_repository)

                total_contribution += _contribution

        if new_repository_list:
            Repository.objects.bulk_create(new_repository_list)

        # 남아 있는 user_repository는 삭제된 repository라 DB에서도 삭제 해준다.
        repo_ids = []
        for repo in user_repositories:
            repo_ids.append(repo.id)

        if repo_ids:
            Repository.objects.filter(id__in=repo_ids).delete()

        self.total_contribution += total_contribution

        return True

    def create_repository(self, user: GithubUser, repository: dict):
        contribution = 0
        new_repository = None

        if repository.get('fork') is True:
            return 0, None

        # User가 이 Repository의 contributor인지 확인한다.
        res = requests.get(repository.get('contributors_url'), headers=self.headers)
        if res.status_code != 200:
            return 0, None

        for contributor in json.loads(res.content.decode("UTF-8")):
            # User 타입이고 contributor 가 본인인 경우
            if contributor.get('type') == 'User' and contributor.get('login') == user.username:
                contribution = contributor.get('contributions')
                languages = ''

                if contribution > 0:
                    languages = self.update_language(repository.get('languages_url'))

                new_repository = Repository(
                    github_user=user,
                    name=repository.get('name'),
                    full_name=repository.get('full_name'),
                    owner=repository.get('owner')['login'],
                    contribution=repository.get('contribution', 0),
                    rep_language=repository.get('language') or '',
                    languages=languages
                )
                break

        return contribution, new_repository

    def create_or_update_language(self, languages_data: dict) -> str:
        """
            프로그램 언어 가져오거나 생성하는 함수
        """
        new_language_list = [] # 새로 추가되는 언어
        for _type, count in languages_data.items():
            if not Language.objects.filter(type=_type).exists():
                new_language_list.append(
                    Language(type=_type)
                )

            if not self.update_language_dict.get(_type):
                self.update_language_dict[_type] = count
            else:
                self.update_language_dict[_type] += count

        if new_language_list:
            Language.objects.bulk_create(new_language_list)

        return json.dumps(list(languages_data.keys()))

    def update_language(self, languages_url: str) -> str:
        """
            repository 에서 사용중인 언어를 찾아서 User 의 사용언어로 추가
        """
        res = requests.get(languages_url, headers=self.headers)
        if res.status_code != 200:
            self.fail_status_code = res.status_code
            return ''

        languages_data = json.loads(res.content.decode("UTF-8"))
        if languages_data:
            return self.create_or_update_language(languages_data)

        return ''

    def update_organization(self, user: GithubUser, organization_url: str) -> bool:
        """
            organization(소속) 업데이트 함
        """

        res = requests.get(organization_url, headers=self.headers)
        if res.status_code != 200:
            self.fail_status_code = res.status_code
            return False

        update_user_organization_list = []
        for organization_data in json.loads(res.content.decode("UTF-8")):
            try:
                organization = Organization.objects.filter(
                    name=organization_data.get('login')
                ).get()

                update_fields = []
                if organization.description != organization_data.get('description'):
                    organization.description = organization_data.get('description')
                    update_fields.append('description')

                if organization.logo != organization_data.get('avatar_url'):
                    organization.logo = organization_data.get('avatar_url')
                    update_fields.append('logo')

                if update_fields:
                    organization.save(update_fields=update_fields)

                update_user_organization_list.append(organization.id)

            except Organization.DoesNotExist:
                description = organization_data.get('description')
                name = organization_data.get('login')
                logo = organization_data.get('avatar_url')

                organization = Organization.objects.create(
                    name=name,
                    logo=logo,
                    description=description if description else '',
                )
                update_user_organization_list.append(organization.id)

            ################################################################################
            #    organization 에 있는 repository 중 User 가 Contributor 인 repository 를 등록한다.
            ################################################################################
            res = requests.get(organization_data.get('repos_url'), headers=self.headers)
            if res.status_code != 200:
                self.fail_status_code = res.status_code
                return False

            for repository in json.loads(res.content.decode("UTF-8")):
                res = requests.get(repository.get('contributors_url'), headers=self.headers)

                if res.status_code != 200:
                    self.fail_status_code = res.status_code
                    return False

                for contributor in json.loads(res.content.decode("UTF-8")):
                    if user.username == contributor.get('login'):
                        self.repositories.append(repository)
                        break

        new_user_organization_list = []
        for organization_id in update_user_organization_list:
            if not UserOrganization.objects.filter(
                    github_user_id=user.id,
                    organization_id=organization_id
            ).exists():
                new_user_organization_list.append(
                    UserOrganization(
                        github_user_id=user.id,
                        organization_id=organization_id
                    )
                )

        if new_user_organization_list:
            UserOrganization.objects.bulk_create(new_user_organization_list)

        return True

    def check_rete_limit(self) -> bool:
        # 현재 호출할 수 있는 rate 체크 (token 있는경우 1시간당 5000번 없으면 60번 호출)
        res = requests.get(GITHUB_RATE_LIMIT_URL, headers=self.headers)

        if res.status_code != 200:
            # 이 경우는 rate_limit api 가 호출이 안되는건데,
            # 이런경우가 깃헙장애 or rate_limit 호출에 제한이 있는지 모르겟다.
            capture_exception(Exception("Can't get RATE LIMIT."))
            return False

        """
            참고: https://docs.gitlab.com/ee/user/admin_area/settings/user_and_ip_rate_limits.html#response-headers
        """
        # 왠만하면 100 이상 호출하는 경우가 있어서 100으로 지정
        content = json.loads(res.content)
        if content['rate']['remaining'] < CHECK_RATE_REMAIN:
            self.fail_status_code = 403
            return False

        return True

    def update(self):
        github_user = None

        result = self.check_rete_limit()
        if not result:
            if not self.is_30_min_script:
                # 큐에 저장해서 따로 실행
                UpdateUserQueue.objects.create(
                    username=self.username,
                    status=UpdateUserQueue.READY
                )
                slack_notify_update_user_queue(self.username)
            return False

        try:
            result, user_information = self.check_github_user()
            if not result:
                return False

            # 1. GithubUser 가 있는지 체크, 없으면 생성
            github_user = self.get_or_create_github_user(user_information)

            # 2. User의 레포지토리 정보르 가져온다
            repo_res = requests.get(user_information.get('repos_url'), headers=self.headers)
            if repo_res.status_code != 200:
                self.fail_status_code = repo_res.status_code
                return False
            self.repositories = json.loads(repo_res.content.decode("UTF-8"))

            # 3. Organization 정보와 연관된 repository 업데이트
            is_update_org = self.update_organization(github_user, user_information.get('organizations_url'))
            if not is_update_org:
                github_user.status = GithubUser.FAIL
                github_user.save(update_fields=['status'])
                return False

            # 4. Repository 정보 업데이트
            is_update_repo = self.update_repositories(github_user)
            if not is_update_repo:
                github_user.status = GithubUser.FAIL
                github_user.save(update_fields=['status'])
                return False

            # 5. language update
            new_user_languages = []
            language_qs = Language.objects.filter(type__in=self.update_language_dict.keys())
            for language in language_qs:
                try:
                    user_language = UserLanguage.objects.filter(
                        github_user_id=github_user.id, language_id=language.id
                    ).get()

                    count = self.update_language_dict.get(language.type)
                    if user_language.number != count:
                        user_language.number = count
                        user_language.save(update_fields=['number'])

                except UserLanguage.DoesNotExist:
                    new_user_languages.append(
                        UserLanguage(
                            github_user_id=github_user.id,
                            language_id=language.id,
                            number=self.update_language_dict.get(language.type)
                        )
                    )

            if new_user_languages:
                UserLanguage.objects.bulk_create(new_user_languages)

        except Exception as e:
            capture_exception(e)
            if github_user:
                github_user.status = GithubUser.COMPLETED
                github_user.save(update_fields=['status'])

            return False

        github_user.status = GithubUser.COMPLETED
        github_user.updated = datetime.now()
        github_user.total_contribution = self.total_contribution
        github_user.save(update_fields=['status', 'updated', 'total_contribution'])

        return github_user
