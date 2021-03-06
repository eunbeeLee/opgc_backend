from datetime import timedelta, datetime

from rest_framework import viewsets, mixins, exceptions
from rest_framework.response import Response
from sentry_sdk import capture_exception

from api.exceptions import NotExistsGithubUser, RateLimitGithubAPI
from api.githubs.serializers import GithubUserSerializer, OrganizationSerializer, RepositorySerializer, \
    LanguageSerializer
from api.paginations import IdOrderingPagination
from apps.githubs.models import GithubUser, Organization, Repository, Language
from utils.exceptions import GitHubUserDoesNotExist, RateLimit
from utils.githubs import GithubInformationService


class GithubUserViewSet(mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
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
            try:
                github_information_service = GithubInformationService(username)
                github_user = github_information_service.update()

            except GitHubUserDoesNotExist:
                raise NotExistsGithubUser()

            except RateLimit:
                raise RateLimitGithubAPI()

            except Exception as e:
                capture_exception(e)

        serializer = self.serializer_class(github_user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        username = self.kwargs.get(self.lookup_url_kwarg)
        response_data = {}

        try:
            github_user = GithubUser.objects.filter(username=username).get()

            # 업데이트 한지 하루가 지나야지 재업데이트
            if github_user.updated + timedelta(1) >= datetime.now():
                response_data = self.serializer_class(github_user).data
                return Response(response_data)

            github_information_service = GithubInformationService(username)
            user = github_information_service.update()
            response_data = self.serializer_class(user).data

        except GithubUser.DoesNotExist:
            raise exceptions.NotFound

        except RateLimit:
            raise RateLimitGithubAPI()

        except Exception as e:
            capture_exception(e)

        return Response(response_data)


class OrganizationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
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


class RepositoryViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
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


class LanguageViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
        endpoint : githubs/languages/
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    pagination_class = IdOrderingPagination
