from django.db import models

from apps.helpers.models import CustomBaseModel


class GithubUser(CustomBaseModel):
    UNRANK, BRONZE, SILVER, GOLD = 0, 5, 10, 15  # 임시
    GITHUB_RANK_CHOICES = (
        (GOLD, 'Gold'),
        (SILVER, 'Silver'),
        (BRONZE, 'bronze'),
        (UNRANK, 'unrank')
    )

    username = models.CharField(unique=True, max_length=200, null=False) # Github ID
    profile_image = models.CharField(max_length=500, null=True)  # Github Profile Image URL
    total_contribution = models.IntegerField(verbose_name='contribution', default=0, db_index=True)
    rank = models.SmallIntegerField(choices=GITHUB_RANK_CHOICES, default=UNRANK, blank=False)
    company = models.CharField(max_length=100, default='', blank=True)
    bio = models.CharField(max_length=200, default='', blank=True) # 설명
    blog = models.CharField(max_length=100, default='', blank=True)
    public_repos = models.IntegerField(default=0, blank=True)
    followers = models.IntegerField(default=0, blank=True)
    following = models.IntegerField(default=0, blank=True)


class Repository(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE, related_name='user')
    contribution = models.IntegerField(verbose_name='contribution', default=0, db_index=True)
    name = models.CharField(max_length=100, blank=False)
    full_name = models.CharField(max_length=100, blank=False)
    owner = models.CharField(max_length=100, blank=False)
    organization = models.CharField(max_length=100, blank=False)


class Language(CustomBaseModel):
    type = models.CharField(verbose_name='language_type', max_length=100, blank=False)


class GithubLanguage(CustomBaseModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE)
    contribution = models.IntegerField(verbose_name='count', default=0)


# 달성 목표 (재미를 위한 컨텐츠)
class Achievements(CustomBaseModel):
    summary = models.CharField(verbose_name='summary', max_length=200, blank=False)
