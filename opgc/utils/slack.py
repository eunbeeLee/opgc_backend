from django.conf import settings
from slackweb import slackweb

from apps.githubs.models import GithubUser


def slack_notify_new_user(user: GithubUser, join_type: str = 'Dirty Boyz'):
    channel = settings.SLACK_CHANNEL_JOINED_USER
    attachments = [
        {
            "color": "#36a64f",
            "title": "유저 등록({})".format(join_type),
            "pretext": "새로운 유저가 등록되었습니다.",
            "fields": [
                {
                    "title": "아이디",
                    "value": user.username,
                    "short": True
                },
                {
                    "title": "설명",
                    "value": user.bio,
                    "short": True
                },
                {
                    "title": "회사",
                    "value": user.company,
                    "short": True
                }
            ],
            "thumb_url": user.profile_image
        }
    ]

    if channel:
        slack = slackweb.Slack(url=channel)
        slack.notify(attachments=attachments)
