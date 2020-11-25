from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response

from api.users.serializers import UserSerializer


class UserViewSet(viewsets.ViewSet, mixins.ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        user_name = self.request.query_params.get('user_name')

        if user_name is None:
            raise exceptions.ParseError

        try:
            queryset = self.queryset.filter().get()
        except User.DoesNotExist:
            raise exceptions.NotFound

        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
