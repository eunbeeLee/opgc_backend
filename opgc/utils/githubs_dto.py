from dataclasses import dataclass


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

    def __init__(self, name: str, full_name: str, owner: str, stargazers_count: int,
                 fork: bool, language: str, contributors_url: str, languages_url: str):
        self.name = name
        self.full_name = full_name
        self.owner = owner
        self.stargazers_count = stargazers_count
        self.fork = fork
        self.language = language
        self.contributors_url = contributors_url
        self.languages_url = languages_url


@dataclass
class OrganizationDto:
    name: str # organization 네임
    description: str # 설명
    logo: str # 프로필(로고)
    repos_url: str # repository URL

    def __init__(self, name: str, description: str, logo: str, repos_url: str):
        self.name = name
        self.description = description
        self.logo = logo
        self.repos_url = repos_url
