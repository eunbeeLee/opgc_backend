from django.conf.urls import url

from api.ranks.views import RankViewSet

app_name = 'ranks'

user_list = RankViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
]
