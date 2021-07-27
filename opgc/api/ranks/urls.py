from django.conf.urls import url

from api.ranks.views import RankViewSet, OverallRankViewSet

app_name = 'ranks'

user_list = RankViewSet.as_view({
    'get': 'list',
})

overall_rank_list = OverallRankViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
    url(r'^overall/$', overall_rank_list, name='overall_rank_list'),
]
