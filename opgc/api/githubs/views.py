from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response

from api.githubs.serializers import GithubUserSerializer
from apps.githubs.models import GithubUser


class GithubUserViewSet(viewsets.ViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """
        endpoint : githubs/users/:username
    """

    queryset = GithubUser.objects.all()
    serializer_class = GithubUserSerializer
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        username = self.kwargs.get(self.lookup_url_kwarg)
        github_user = GithubUser.objects.filter(username=username).get()
        return github_user

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except GithubUser.DoesNotExist:
            # todo: user가 없는 경우 생성하도록 처리하고 client에는 잠시기다리라는 안내?하기
            raise exceptions.NotFound

        serializer = self.serializer_class(queryset)
        return Response(serializer.data)
