from datetime import datetime

from django.db import models


class CustomBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.reg_time = datetime.now()
        self.mod_time = datetime.now()
        return super().save(*args, **kwargs)
