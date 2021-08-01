from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.githubs.models import GithubUser


class UserProfileView(View):

    def get(self, request, **kwargs):
        username = request.GET.get('username')
        github_user = get_object_or_404(GithubUser, username=username)
        return render(request, 'user_profile/profile.html', {'github_user': github_user})
