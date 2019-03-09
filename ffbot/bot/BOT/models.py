from django.db import models

# Create your models here.

class Class(models.Model):
    name = models.CharField(max_length=15)
    nick = models.CharField(max_length=100)
    fflog_id = models.IntegerField()