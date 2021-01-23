from django.db import models

from apps.helpers.models import CustomBaseModel


class UpdateUserQueue(CustomBaseModel):
    READY, FAIL, PROGRESSING = 0, 5, 10
    UPDATING_STATUS = (
        (READY, 'ready'),
        (FAIL, 'fail'),
        (PROGRESSING, 'progressing')
    )

    username = models.CharField(max_length=200, null=False)
    status = models.SmallIntegerField(choices=UPDATING_STATUS, default=READY, blank=False)

    class Meta:
        verbose_name = 'update_user_queue'
