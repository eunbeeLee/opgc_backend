from django.db import models

from apps.helpers.models import CustomBaseModel
from apps.users.models import User

"""
시즌(년도)마다 github information 모델 생성
"""


class GithubUserInformation(CustomBaseModel):
    UNRANK, BRONZE, SILVER, GOLD = 0, 5, 10, 15  # 임시
    GITHUB_RANK_CHOICES = (
        (GOLD, 'Gold'),
        (SILVER, 'Silver'),
        (BRONZE, 'bronze'),
        (UNRANK, 'unrank')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    total_contribution = models.IntegerField(verbose_name='contribution', default=0, db_index=True)
    rank = models.SmallIntegerField(choices=GITHUB_RANK_CHOICES, default=UNRANK, blank=False)


class Language(CustomBaseModel):
    type = models.CharField(verbose_name='language_type', max_length=100, blank=False)


class GithubLanguage(CustomBaseModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    github_user = models.ForeignKey(GithubUserInformation, on_delete=models.CASCADE)
    contribution = models.IntegerField(verbose_name='count', default=0)


# 달성 목표 (재미를 위한 컨텐츠)
class Achievements(CustomBaseModel):
    summary = models.CharField(verbose_name='summary', max_length=200, blank=False)
