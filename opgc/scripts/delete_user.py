from django.db import transaction

from apps.githubs.models import GithubUser, UserLanguage, UserOrganization
from apps.ranks.models import UserRank
from apps.reservations.models import UpdateUserQueue

USERNAME = 'zzsza'


def run():
    with transaction.atomic():
        github_user = GithubUser.objects.get(username=USERNAME)
        UserLanguage.objects.filter(github_user_id=github_user.id).delete()
        UserOrganization.objects.filter(github_user_id=github_user.id).delete()
        UpdateUserQueue.objects.filter(username=github_user.username).delete()
        UserRank.objects.filter(github_user_id=github_user.id).update(github_user=None)
        github_user.delete()
