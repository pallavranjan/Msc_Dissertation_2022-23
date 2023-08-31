from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering=('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name