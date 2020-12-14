from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Task(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="task_owner")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True)
    description = models.TextField()
    selected = models.BooleanField(default=False)
    completion_time = models.TextField(default=0)
    completion_date = models.DateField(null=True)
    current_task_time = models.TextField(default=0)

class Project(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="project_owner")
    project_title = models.TextField()
    anticipated_completion_date = models.DateField(null=True)
    completion_date = models.DateField(null=True)

class Reminder(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="reminder_owner")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True)
    description = models.TextField()
    reminder_date = models.DateField(null=True)
    completion_date = models.DateField(null=True)