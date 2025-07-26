from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=100)
    count_access_token = models.IntegerField(default=2)
    def __str__(self):
        return self.name

