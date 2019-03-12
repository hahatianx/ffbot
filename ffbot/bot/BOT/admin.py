from django.contrib import admin
from bot.BOT import models

# Register your models here.
admin.site.register(models.Class)
class ClassAdmin(admin.ModelAdmin):
    def __init__(self):
        pass


admin.site.register(models.NickClass)
class NickClassAdmin(admin.ModelAdmin):
    def __init__(self):
        pass


admin.site.register(models.Boss)
class BossAdmin(admin.ModelAdmin):
    def __init__(self):
        pass


admin.site.register(models.NickBoss)
class NickBossAdmin(admin.ModelAdmin):
    def __init__(self):
        pass
