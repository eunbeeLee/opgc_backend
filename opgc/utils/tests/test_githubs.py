from unittest import mock

import pytest
from utils.githubs import GithubInformationService


@pytest.fixture(scope='function')
def mock_slack_notify_new_user():
    with mock.patch('utils.githubs.slack_notify_new_user') as patch:
        yield patch


@pytest.mark.urls(urls='conf.urls.api')
@pytest.mark.django_db
def test_get_or_create_github_user(github_context, mock_slack_notify_new_user):
    username = 'JAY-Chan9yu'
    test_user_information = {
        'username': username,
        'name': 'jay',
        'email': 'jay@test.com',
        'location': 'Republic of Korea',
        'avatar_url': 'https://avatars.githubusercontent.com/u/24591259?v=4',
        'company': 'DirtyBoyz',
        'bio': '',
        'blog': '',
        'public_repos': 0,
        'followers': 0,
        'following': 0,
    }

    github_information_service = GithubInformationService(username=username)
    github_user = github_information_service.get_or_create_github_user(test_user_information)

    assert github_user is not None
    for key, value in test_user_information.items():
        assert getattr(github_user, key, None) == value
