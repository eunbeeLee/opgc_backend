from rest_framework import viewsets, mixins, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.githubs.serializers import GithubUserSerializer, OrganizationSerializer
from apps.githubs.models import GithubUser, Organization, UserOrganization


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

        try:
            github_user = GithubUser.objects.filter(username=username).get()
        except GithubUser.DoesNotExist:
            raise exceptions.NotFound

        return github_user

    def list(self, request, *args, **kwargs):
        # todo: user가 없는 경우 생성하도록 처리하고 client에는 잠시기다리라는 안내?하기
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)

        return Response(serializer.data)


class OrganizationViewSet(viewsets.ViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin):
    """
        endpoint : githubs/users/:user_pk/organizations/
    """

    queryset = Organization.objects.all()
    serializer_class = GithubUserSerializer
    lookup_url_kwarg = 'user_pk'

    def get_queryset(self):
        user_pk = int(self.kwargs.get(self.lookup_url_kwarg))
        organizations = Organization.objects.filter(org__github_user_id=user_pk)

        return organizations

    def list(self, request, *args, **kwargs):
        organizations = self.get_queryset()
        serializer = OrganizationSerializer(organizations, many=True)

        return Response(serializer.data)
