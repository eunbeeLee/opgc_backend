from django.db import transaction

from apps.githubs.models import GithubUser, UserLanguage, UserOrganization

USERNAME = 'usesrname'


def run():
    with transaction.atomic():
        github_user = GithubUser.objects.filter(username=USERNAME).get().select_for_update()
        UserLanguage.objects.filter(github_user_id=github_user.id).delete()
        UserOrganization.objects.filter(github_user_id=github_user.id).delete()
        github_user.delete()
