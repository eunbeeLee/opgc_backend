from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response

from api.githubs.serializers import GithubUserSerializer, OrganizationSerializer, RepositorySerializer
from apps.githubs.models import GithubUser, Organization, Repository
from utils.githubs import UpdateGithubInformation


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
            # todo: GithubUser 에 updated(datetime) 필드 추가 후 업데이트 시간 체크해서 업데이트 하는 로직 추가
        except GithubUser.DoesNotExist:
            update_github_information = UpdateGithubInformation(username)
            exists, user_information = update_github_information.check_github_user()

            if not exists:
                raise exceptions.NotFound

            # todo: GithubUser 정보만 업데이트하고 나머지 따로 처리할건지 생각해야함 (오래걸림 작업이)
            github_user = update_github_information.update(user_information=user_information)

        if not isinstance(github_user, GithubUser):
            raise exceptions.NotFound

        return github_user

    def list(self, request, *args, **kwargs):
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
        user_pk = self.kwargs.get(self.lookup_url_kwarg)
        organizations = Organization.objects.filter(org__github_user_id=user_pk)

        return organizations

    def list(self, request, *args, **kwargs):
        organizations = self.get_queryset()
        serializer = OrganizationSerializer(organizations, many=True)

        return Response(serializer.data)


class RepositoryViewSet(viewsets.ViewSet,
                        mixins.ListModelMixin):
    """
        endpoint : githubs/:user_pk/repositories/
    """

    queryset = Repository.objects.all()
    serializer_class = GithubUserSerializer
    lookup_url_kwarg = 'user_pk'

    def get_queryset(self):
        user_pk = self.kwargs.get(self.lookup_url_kwarg)
        repositories = Repository.objects.filter(github_user_id=user_pk)

        return repositories

    def list(self, request, *args, **kwargs):
        organizations = self.get_queryset()
        serializer = RepositorySerializer(organizations, many=True)

        return Response(serializer.data)
