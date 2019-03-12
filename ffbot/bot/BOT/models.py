from django.db import models

# Create your models here.


class Class(models.Model):
    name = models.CharField(max_length=15)


class NickClass(models.Model):
    nick_name = models.CharField(max_length=15)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, default='')


class Boss(models.Model):
    name = models.CharField(max_length=15)
    quest_id = models.IntegerField()
    boss_id = models.IntegerField()


class NickBoss(models.Model):
    nick_name = models.CharField(max_length=15)
    boss_id = models.ForeignKey(Boss, on_delete=models.CASCADE, default='')
