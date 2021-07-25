from rest_framework import mixins, viewsets

from api.notices.serializers import NoticeSerializer
from api.paginations import DescIdOrderingPagination
from apps.notices.models import Notice


class NoticeViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    endpoint : notice/
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    pagination_class = DescIdOrderingPagination
