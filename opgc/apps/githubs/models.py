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
    total_contribution = models.IntegerField(verbose_name='contribution', default=0)
    rank = models.SmallIntegerField(choices=GITHUB_RANK_CHOICES, default=UNRANK, blank=False)
    company = models.CharField(max_length=100, default='', blank=True)
    bio = models.CharField(max_length=200, default='', blank=True) # 설명
    blog = models.CharField(max_length=100, default='', blank=True)
    public_repos = models.IntegerField(default=0, blank=True)
    followers = models.IntegerField(default=0, blank=True)
    following = models.IntegerField(default=0, blank=True)


class Language(CustomBaseModel):
    type = models.CharField(verbose_name='language_type', unique=True, max_length=100, blank=False)


class Organization(CustomBaseModel):
    name = models.CharField(verbose_name='name', unique=True, max_length=100, blank=False)
    description = models.CharField(verbose_name='description', max_length=500, blank=False)
    logo = models.CharField(max_length=500, null=True)


class UserOrganization(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Repository(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE, related_name='user')
    contribution = models.IntegerField(verbose_name='contribution', default=0)
    name = models.CharField(max_length=100, blank=False)
    full_name = models.CharField(max_length=100, blank=False)
    owner = models.CharField(max_length=100, blank=False)
    organization = models.CharField(max_length=100, blank=False)
    language = models.ForeignKey(Language,
                                 on_delete=models.DO_NOTHING,
                                 default=None,
                                 null=True,
                                 blank=True,
                                 related_name='language')


class GithubLanguage(CustomBaseModel):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE)
    number = models.IntegerField(default=0) # number of bytes of code written in that language.


# 달성 목표 (재미를 위한 컨텐츠)
class Achievements(CustomBaseModel):
    summary = models.CharField(verbose_name='summary', max_length=200, blank=False)
