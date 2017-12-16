from django.db import models

from .enums import BaseEnum

class EnumField(models.PositiveSmallIntegerField):
    def __init__(self, *args, **kwargs):
        self.enumClass = kwargs['enum_class']
        del kwargs['enum_class']
        kwargs.update(choices=self.enumClass.choices())

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        kwargs['enum_class'] = self.enumClass
        return name, path, args, kwargs

    def get_enum_name(self):
        return self.enumClass(self).name