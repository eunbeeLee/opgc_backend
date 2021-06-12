import asyncio
import json
from dataclasses import dataclass

import aiohttp
import requests
from django.conf import settings

from apps.githubs.models import GithubUser, Repository, Language, UserLanguage
from utils.exceptions import manage_api_call_fail


@dataclass
class RepositoryDto:
    name: str # 레포지토리 네임
    full_name: str # 레포지토리 풀네임
    owner: str # 소유자(?)
    stargazers_count: int # start 카운트
    fork: bool # fork 여부
    language: str # 대표 언어
    contributors_url: str  # contributor 정보 URL
    languages_url: str  # 언어 정보 URL

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.full_name = kwargs.get('full_name')
        self.owner = kwargs.get('owner').get('login')
        self.stargazers_count = kwargs.get('stargazers_count')
        self.fork = kwargs.get('fork')
        self.language = kwargs.get('language', '')
        self.contributors_url = kwargs.get('contributors_url')
        self.languages_url = kwargs.get('languages_url')


class RepositoryService(object):

    def __init__(self, github_user: GithubUser):
        self.github_user = github_user
        self.total_contribution = 0
        self.total_stargazers_count = 0
        self.repositories = [] # 업데이트할 레포지토리 리스트
        self.new_repository_list = [] # 새로 생성될 레포지토리 리스트
        self.update_language_dict = {} # 업데이트할 language

    def create_dto(self, repository_data: dict) -> RepositoryDto:
        return RepositoryDto(**repository_data)

    def update_repositories(self) -> bool:
        """
            레포지토리 업데이트 함수
        """
        # 유저의 현재 모든 repository를 가져온다.
        user_repositories = list(Repository.objects.filter(github_user=self.github_user))

        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.update_repository_futures(self.repositories, user_repositories))

        if self.new_repository_list:
            Repository.objects.bulk_create(self.new_repository_list)

        # 남아 있는 user_repository는 삭제된 repository라 DB에서도 삭제 해준다.
        repo_ids = []
        for repo in user_repositories:
            repo_ids.append(repo.id)

        if repo_ids:
            Repository.objects.filter(id__in=repo_ids).delete()

        return True

    def create_repository(self, repository: RepositoryDto):
        contribution = 0
        new_repository = None

        if repository.fork is True:
            return 0, None

        # User가 Repository의 contributor 인지 확인한다.
        res = requests.get(repository.contributors_url, headers=settings.GITHUB_API_HEADER)
        if res.status_code != 200:
            manage_api_call_fail(self.github_user, res.status_code)

        try:
            contributors = json.loads(res.content)
        except json.JSONDecodeError:
            return contribution, new_repository

        for contributor in contributors:
            # User 타입이고 contributor 가 본인인 경우
            if contributor.get('type') == 'User' and contributor.get('login') == self.github_user.username:
                contribution = contributor.get('contributions', 0)
                languages = ''

                if contribution > 0:
                    languages = self.record_language(repository.languages_url)

                new_repository = Repository(
                    github_user=self.github_user,
                    name=repository.name,
                    full_name=repository.full_name,
                    owner=repository.owner,
                    contribution=contribution,
                    stargazers_count=repository.stargazers_count,
                    rep_language=repository.language,
                    languages=languages
                )
                self.total_stargazers_count += repository.stargazers_count
                break

        return contribution, new_repository

    def record_language(self, languages_url: str) -> str:
        """
            repository 에서 사용중인 언어를 찾아서 dictionary에 type과 count를 저장
            - count : 해당 언어로 작성된 코드의 바이트 수.
        """

        res = requests.get(languages_url, headers=settings.GITHUB_API_HEADER)
        if res.status_code != 200:
            manage_api_call_fail(self.github_user, res.status_code)

        try:
            languages_data = json.loads(res.content)
        except json.JSONDecodeError:
            return ''

        if languages_data:
            for _type, count in languages_data.items():
                if not self.update_language_dict.get(_type):
                    self.update_language_dict[_type] = count
                else:
                    self.update_language_dict[_type] += count

            return json.dumps(list(languages_data.keys()))

        return ''

    def update_or_create_language(self):
        """
            새로 추가된 언어를 만들고 User가 사용하는 언어사용 count(byte 수)를 업데이트 해주는 함수
        """

        # DB에 없던 Language 생성
        new_language_list = []
        exists_languages = set(Language.objects.filter(
            type__in=self.update_language_dict.keys()).values_list('type', flat=True))
        new_languages = set(self.update_language_dict.keys()) - exists_languages

        for language in new_languages:
            new_language_list.append(Language(type=language))

        if new_language_list:
            Language.objects.bulk_create(new_language_list)

        # 가존에 있던 UserLanguage 업데이트
        new_user_languages = []
        user_language_qs = UserLanguage.objects.prefetch_related('language').filter(
            github_user_id=self.github_user.id, language__type__in=self.update_language_dict.keys()
        )
        for user_language in user_language_qs:
            if user_language.language.type in self.update_language_dict.keys():
                count = self.update_language_dict.pop(user_language.language.type)

                if user_language.number != count:
                    user_language.number = count
                    user_language.save(update_fields=['number'])

        # 새로운 UserLanguage 생성
        languages = Language.objects.filter(type__in=self.update_language_dict.keys())
        for language in languages:
            new_user_languages.append(
                UserLanguage(
                    github_user_id=self.github_user.id,
                    language_id=language.id,
                    number=self.update_language_dict.pop(language.type)
                )
            )

        if new_user_languages:
            UserLanguage.objects.bulk_create(new_user_languages)

    async def update_repository(self, repository: RepositoryDto, user_repositories: list):  # 코루틴 정의
        is_exist_repo = False

        for idx, user_repo in enumerate(user_repositories):
            if user_repo.full_name == repository.full_name and user_repo.owner == repository.owner:
                is_exist_repo = True
                user_repositories.pop(idx)
                update_fields = []
                contribution = 0

                # User가 Repository의 contributor 인지 확인한다.
                async with aiohttp.ClientSession() as session:
                    async with session.get(repository.contributors_url, headers=settings.GITHUB_API_HEADER) as res:
                        response_data = await res.text()
                        response_status = res.status

                if response_status == 200:
                    for contributor in json.loads(response_data):
                        # User 타입이고 contributor 가 본인인 경우
                        if contributor.get('type') == 'User' and contributor.get('login') == self.github_user.username:
                            contribution = contributor.get('contributions')
                            # languages number update
                            self.record_language(repository.languages_url)

                # repository update
                if user_repo.contribution != contribution:
                    user_repo.contribution = contribution
                    update_fields.append('contribution')

                # repository update
                if user_repo.stargazers_count != repository.stargazers_count:
                    user_repo.stargazers_count = repository.stargazers_count
                    update_fields.append('stargazers_count')

                if update_fields:
                    user_repo.save(update_fields=update_fields)

                self.total_stargazers_count += repository.stargazers_count
                self.total_contribution += contribution
                break

        # 새로운 레포지토리
        if not is_exist_repo:
            _contribution, new_repository = self.create_repository(repository)

            if new_repository:
                self.new_repository_list.append(new_repository)

            self.total_contribution += _contribution

    async def update_repository_futures(self, repositories, user_repositories: list):
        futures = [asyncio.ensure_future(
            self.update_repository(repository, user_repositories)) for repository in repositories
        ]

        await asyncio.gather(*futures)