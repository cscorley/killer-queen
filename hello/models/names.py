from django.db import models

class RandomName(models.Model):
    name = models.CharField('name', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
