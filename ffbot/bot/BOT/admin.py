from django.contrib import admin
from bot.BOT import models

# Register your models here.
admin.site.register(models.Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(models.NickClass)
class NickClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'nick_name', 'class_id')


admin.site.register(models.Boss)
class BossAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'quest_id', 'boss_id', 'add_time')


admin.site.register(models.NickBoss)
class NickBossAdmin(admin.ModelAdmin):
    list_display = ('id', 'nick_name', 'boss_id')
