from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.notices.views import NoticeViewSet

app_name = 'notices'
notice_list = NoticeViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^$', notice_list, name='notice_list'),
]

# router = DefaultRouter()
# router.register(r'', NoticeViewSet, basename='notice')
#
# urlpatterns = [
#     path(r'', include(router.urls)),
# ]
