from django.conf.urls import url

from api.githubs.views import GithubUserViewSet, OrganizationViewSet, RepositoryViewSet

app_name = 'githubs'

github_user_list = GithubUserViewSet.as_view({
    'get': 'list',
})

organization_list = OrganizationViewSet.as_view({
    'get': 'list',
})

repository_list = RepositoryViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^users/(?P<username>[-\w]+)/$', github_user_list, name='github_user_list'),
    url(r'^users/(?P<user_pk>\d+)/organizations/$', organization_list, name='organization_list'),
    url(r'^users/(?P<user_pk>\d+)/repositories/$', repository_list, name='repository_list'),
]
