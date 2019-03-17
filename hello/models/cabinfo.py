from django.db import models

class CabInformation(models.Model):
    name = models.CharField('name', max_length=255, primary_key=True)
    json = models.TextField('json')
    updated = models.DateTimeField('date last updated', auto_now=True)

    def __str__(self) -> str:
        return "%s: %s..." % (self.name, self.json[:15])
