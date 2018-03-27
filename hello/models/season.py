from django.db import models

class Season(models.Model):
    name = models.CharField('name', max_length=255)


    def __str__(self) -> str:
        return "%s" % (self.name)
