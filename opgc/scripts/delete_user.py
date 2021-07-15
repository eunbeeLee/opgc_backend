from django.db import transaction

from apps.githubs.models import GithubUser, UserLanguage, UserOrganization
from apps.ranks.models import UserRank
from apps.reservations.models import UpdateUserQueue


def run():
    username = input("input delete username: ")
    answer = input("Are you sure you want to delete it?(y or n): ")

    if answer == 'y':
        with transaction.atomic():
            github_user = GithubUser.objects.get(username=username)
            UserLanguage.objects.filter(github_user_id=github_user.id).delete()
            UserOrganization.objects.filter(github_user_id=github_user.id).delete()
            UpdateUserQueue.objects.filter(username=github_user.username).delete()
            UserRank.objects.filter(github_user_id=github_user.id).invalidated_update(github_user=None)
            github_user.delete()
