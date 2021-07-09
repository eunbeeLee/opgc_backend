from django.conf.urls import url

from api.githubs.views import GithubUserViewSet, OrganizationViewSet, RepositoryViewSet, LanguageViewSet, \
    TierRankViewSet, UserRankViewSet

app_name = 'githubs'

# todo: 라우터로 변경, 유저 리스트 파라미터 타입으로 구분하도록 수정

github_user_list = GithubUserViewSet.as_view({
    'get': 'retrieve',
    'patch': 'update'
})

organization_list = OrganizationViewSet.as_view({
    'get': 'list',
})

repository_list = RepositoryViewSet.as_view({
    'get': 'list',
})

language_list = LanguageViewSet.as_view({
    'get': 'list',
})

tier_list = TierRankViewSet.as_view({
    'get': 'list',
})

user_rank_list = UserRankViewSet.as_view({
    'get': 'list',
})


urlpatterns = [
    url(r'^users/(?P<username>[-\w]+)/$', github_user_list, name='github_user_list'),
    url(r'^users/(?P<user_pk>\d+)/organizations/$', organization_list, name='organization_list'),
    url(r'^users/(?P<user_pk>\d+)/repositories/$', repository_list, name='repository_list'),
    url(r'^languages/$', language_list, name='language_list'),
    url(r'^tier/$', tier_list, name='tier_list'),
    url(r'^user_rank/$', user_rank_list, name='user_rank_list'),
]
