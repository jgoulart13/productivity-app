# Generated by Django 3.0.3 on 2020-08-09 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task_project_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='project_title',
            field=models.TextField(default='None', null=True),
        ),
    ]
