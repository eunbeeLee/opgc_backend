from django.db import models


class CustomModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(CustomModel):
    username = models.CharField(unique=True, max_length=200, null=False) # Github ID
    profile_image = models.CharField(max_length=500, null=True) # Github Profile Image URL
