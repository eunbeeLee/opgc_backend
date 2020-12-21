from django.db import models

from apps.helpers.models import CustomBaseModel


class Reservation(CustomBaseModel):
    READY, FAIL = 0, 5
    UPDATING_STATUS = (
        (READY, 'ready'),
        (FAIL, 'fail')
    )

    user_idx = models.PositiveIntegerField(db_index=True)
    status = models.SmallIntegerField(choices=UPDATING_STATUS, default=READY, blank=False)
