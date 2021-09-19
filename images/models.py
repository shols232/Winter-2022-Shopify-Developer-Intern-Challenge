from django.contrib.auth.models import User
from django.db import models

from lib.models import BaseAbstractModel


class UserImage(BaseAbstractModel):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False)
    image = models.FileField(null=False, blank=False)
    times_shared = models.IntegerField(default=0)
    size = models.IntegerField()

    def save(self, *args, **kwargs):
        self.size = self.image.size
        super().save(*args, **kwargs)

    def __str__(self):
        return "ImageName: {} - Owner: {}".format(self.image.name, self.owner.username)
