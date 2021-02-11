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

    NONE, COMPLETED, WAITING, UPDATING, FAIL = 0, 5, 10, 15, 20
    UPDATING_STATUS = (
        (NONE, 'none'),
        (COMPLETED, 'completed'),
        (WAITING, 'waiting'),
        (UPDATING, 'updating'),
        (FAIL, 'fail')
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
    status = models.SmallIntegerField(choices=UPDATING_STATUS, default=NONE, blank=False)


class Language(CustomBaseModel):
    type = models.CharField(verbose_name='language_type', unique=True, max_length=100, blank=False)
    github_users = models.ManyToManyField(GithubUser, through='UserLanguage', related_name='language', blank=True)

    def __str__(self):
        return f'{self.type}'


class UserLanguage(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, db_constraint=False, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, db_constraint=False, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)  # number of bytes of code written in that language.

    class Meta:
        db_table = 'githubs_user_language'
        verbose_name = 'user language'


class Organization(CustomBaseModel):
    name = models.CharField(verbose_name='name', unique=True, max_length=100, blank=False)
    description = models.CharField(verbose_name='description', max_length=500, blank=False)
    logo = models.CharField(max_length=500, null=True)
    github_users = models.ManyToManyField(GithubUser, through='UserOrganization', related_name='organization', blank=True)


class UserOrganization(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, db_constraint=False, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, db_constraint=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'githubs_user_organization'
        verbose_name = 'user organization'


class Repository(CustomBaseModel):
    github_user = models.ForeignKey(GithubUser, on_delete=models.CASCADE, related_name='repository')
    contribution = models.IntegerField(verbose_name='contribution', default=0)
    name = models.CharField(max_length=100, blank=False)
    full_name = models.CharField(max_length=100, blank=False)
    owner = models.CharField(max_length=100, blank=False)
    organization = models.CharField(max_length=100, blank=False)
    rep_language = models.CharField(max_length=100, blank=False, default='') # 대표언어
    languages = models.CharField(max_length=1000, blank=False, default='') # 레포지토리에서 사용하는 모든 언어(json)


class Achievements(CustomBaseModel): # 달성 목표 (재미를 위한 컨텐츠)
    summary = models.CharField(verbose_name='summary', max_length=200, blank=False)
