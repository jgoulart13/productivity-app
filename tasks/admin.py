from django.contrib import admin

# Register your models here.
from .models import Task, Project, Reminder

admin.site.register(Task)
admin.site.register(Project)
admin.site.register(Reminder)
