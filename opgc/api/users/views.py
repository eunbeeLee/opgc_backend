from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response

from api.users.serializers import UserSerializer
from apps.users.models import User

"""
    todo: 사용 안함
"""
class UserViewSet(viewsets.ViewSet, mixins.ListModelMixin):
    """
        endpoint : users/
        : 여기서 User는 따로 Oauth 인증같은건 하지 않는다. 단순히 username만 저장함
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        user_name = self.request.query_params.get('user_name')

        if user_name is None:
            raise exceptions.ParseError

        try:
            queryset = self.queryset.filter(username=user_name).get()
        except User.DoesNotExist:
            raise exceptions.NotFound

        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
