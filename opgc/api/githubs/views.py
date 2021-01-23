from datetime import timedelta, datetime

from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response

from api.githubs.serializers import GithubUserSerializer, OrganizationSerializer, RepositorySerializer
from apps.githubs.models import GithubUser, Organization, Repository
from utils.githubs import UpdateGithubInformation


class GithubUserViewSet(viewsets.ViewSet,
                        mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin):
    """
        endpoint : githubs/users/:username
    """

    queryset = GithubUser.objects.prefetch_related(
        'organization', 'repository'
    ).all()
    serializer_class = GithubUserSerializer
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        username = self.kwargs.get(self.lookup_url_kwarg)

        try:
            github_user = GithubUser.objects.filter(username=username).get()
        except GithubUser.DoesNotExist:
            return None

        return github_user

    def list(self, request, *args, **kwargs):
        username = self.kwargs.get(self.lookup_url_kwarg)
        github_user = self.get_queryset()

        if github_user is None:
            update_github_information = UpdateGithubInformation(username)
            github_user = update_github_information.update()

            if not github_user:
                # github_user가 없거나 rate_limit로 인해 업데이트를 할 수 없는경우
                data = {
                    'error': 'rate_limit',
                    'content': 'Github api호출이 가능한 시점이 되면 유저정보를 생성하거나 업데이트합니다.'
                }
                return Response(data, status=400)

        serializer = self.serializer_class(github_user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        username = self.kwargs.get(self.lookup_url_kwarg)

        try:
            github_user = GithubUser.objects.filter(username=username).get()

            # 업데이트 한지 하루가 지나야지 재업데이트
            if github_user.updated + timedelta(1) >= datetime.now():
                serializer = self.serializer_class(github_user)
                return Response(serializer.data, status=400)

        except GithubUser.DoesNotExist:
            raise exceptions.NotFound

        update_github_information = UpdateGithubInformation(username)
        user = update_github_information.update()
        if not user:
            # 깃헙 api를 호출할 수 없는경우 (rate_limit)
            serializer = self.serializer_class(github_user)
            return Response(serializer.data, status=400)

        serializer = self.serializer_class(user)

        return Response(serializer.data)


class OrganizationViewSet(viewsets.ViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin):
    """
        endpoint : githubs/users/:user_pk/organizations/
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_url_kwarg = 'user_pk'

    def get_queryset(self):
        user_pk = self.kwargs.get(self.lookup_url_kwarg)
        organizations = Organization.objects.filter(org__github_user_id=user_pk)

        return organizations

    def list(self, request, *args, **kwargs):
        organizations = self.get_queryset()
        serializer = self.serializer_class(organizations, many=True)

        return Response(serializer.data)


class RepositoryViewSet(viewsets.ViewSet,
                        mixins.ListModelMixin):
    """
        endpoint : githubs/:user_pk/repositories/
    """

    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    lookup_url_kwarg = 'user_pk'

    def get_queryset(self):
        user_pk = self.kwargs.get(self.lookup_url_kwarg)
        repositories = Repository.objects.filter(github_user_id=user_pk)

        return repositories

    def list(self, request, *args, **kwargs):
        repositories = self.get_queryset()
        serializer = self.serializer_class(repositories, many=True)

        return Response(serializer.data)
