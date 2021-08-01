from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View
from html2image import Html2Image

from apps.githubs.models import GithubUser


class UserProfileView(View):

    def get(self, request, **kwargs):
        username = request.GET.get('username')
        try:
            github_user = GithubUser.objects.get(username=username)
        except GithubUser.DoesNotExist:
            raise Http404

        # todo: 코드 정리하기
        html = f"""
            <div class="profile-base">
                <div class="rank">
                    <img src="https://www.opgc.me/assets/imgs/tier-{github_user.get_tier_display().lower()}.png" width="100" height="100">
                </div>
                <div class="inform">
                    <ul>
                        <li>My OPGC Profile</li>
                        <li>🏆&nbsp;&nbsp;Rank: {github_user.user_rank}</li>
                        <li>📈&nbsp;&nbsp;Total Score: {github_user.total_score}</li>
                        <li>🌱&nbsp;&nbsp;1day 1commit: {github_user.continuous_commit_day}</li>
                    </ul>
                </div>
            </div>
        """

        css = """
            .profile-base {
                background: white;
                display: flex;
                max-width: 300px;
                font-size: small;
                border: 1px solid;
                border-radius: 10px;
                padding: 15px;
                -webkit-box-shadow: 0 0 10px -1px grey;
                -moz-box-shadow: 0 0 10px -1px grey;
                box-shadow: 0 0 10px -1px grey;
            }
    
            .rank {
                vertical-align:middle;
            }
    
            .opgc-link {
                color: #29855b;
            }
    
            .inform {
                margin-left: 10px;
                width: 100%;
            }
    
            .profile-base ul {
                margin: 10px;
                list-style: none;
                padding-left: 0;
                display: inline-block;
            }
    
            .profile-base li {
                margin-bottom: 3px;
            }
        """

        hti = Html2Image(output_path=settings.PROFILE_IMAGE_DIR)
        hti.screenshot(html_str=html, css_str=css, save_as=f'{username}.png', size=(320, 160))

        img = open(f'{settings.PROFILE_IMAGE_DIR}/{username}.png', 'rb')
        response = FileResponse(img)

        return response
