from django.contrib import admin
from bot.BOT import models

# Register your models here.
admin.site.register(models.Class)
class ClassAdmin(admin.ModelAdmin):
    def __init__(self):
        pass

