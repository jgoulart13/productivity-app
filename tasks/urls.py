
from django.urls import path, register_converter
from datetime import datetime
from . import views

class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value

register_converter(DateConverter, 'yyyy')

urlpatterns = [
    path("", views.index, name="index"),
    path("backlog", views.backlog_view, name="backlog"),
    path("update", views.complete, name="update"),
    path("complete/all", views.completed, name="complete"),
    path("complete/date/<yyyy:date>/", views.completedate, name="completedate"),
    path("daily", views.daily_view, name="daily"),
    path("create", views.create, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("pause/", views.pause, name="pause"),
    path("project/<int:project_id>", views.project_view, name="project"),
    path("project/remove", views.remove, name="remove"),
    path("register", views.register_view, name="register"),
    path("select/<int:task_id>", views.select, name="select"),
    path("start/", views.start, name="start"),
    path("taskchart/", views.task_chart, name="task-chart"),
    path("timechart/", views.time_chart, name="time-chart")
]
