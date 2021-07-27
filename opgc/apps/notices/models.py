from django.db import models

from core.models import CustomBaseModel


class Notice(CustomBaseModel):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)

    class Meta:
        db_table = 'notice'
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항'

