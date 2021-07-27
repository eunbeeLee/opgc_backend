from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.notices.views import NoticeViewSet

app_name = 'notices'

router = DefaultRouter()
router.register(r'', NoticeViewSet, basename='notice')

urlpatterns = [
    path(r'', include(router.urls)),
]
