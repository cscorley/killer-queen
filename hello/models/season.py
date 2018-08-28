from django.db import models

class Season(models.Model):
    name = models.CharField('name', max_length=255)
    created = models.DateTimeField('date created', auto_now_add=True)
    when = models.DateTimeField('season start time', auto_now_add=False)

    def __str__(self) -> str:
        return "%s" % (self.name)
