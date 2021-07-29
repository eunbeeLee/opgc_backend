from rest_framework import mixins, viewsets

from api.notices.serializers import NoticeSerializer, NoticeListSerializer
from api.paginations import DescIdOrderingPagination
from apps.notices.models import Notice


class NoticeViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    endpoint : notice/
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    pagination_class = DescIdOrderingPagination

    def list(self, request, *args, **kwargs):
        self.serializer_class = NoticeListSerializer
        return super().list(request, *args, **kwargs)
