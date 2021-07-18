from django.db import transaction

from apps.githubs.models import GithubUser
from apps.reservations.models import UpdateUserQueue


def run():
    username = input("input delete username: ")
    answer = input("Are you sure you want to delete it?(y or n): ")

    try:
        github_user = GithubUser.objects.get(username=username)

        if answer == 'y':
            with transaction.atomic():
                github_user.delete()
                UpdateUserQueue.objects.filter(username=github_user.username).delete()

    except GithubUser.DoesNotExist:
        print(f'{username} dose not exist!')
