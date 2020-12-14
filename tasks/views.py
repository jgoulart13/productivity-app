import json
from datetime import datetime, date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Avg, Count, FloatField, IntegerField, F
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse


from .models import  Project, Reminder, Task, User

# Route for the homepage
def index(request):
    return render(request, "tasks/homepage.html")

@login_required
# Route for backlog view that displays projects as well as a link to tasks/reminders with no projects
def backlog_view(request):

    # Generate kwargs with impossible project id
    max_project_id = Project.objects.all().order_by("-id")[0].id
    impossible_project_id = max_project_id+1
    
    return render(request, "tasks/backlog.html",{
        "user": request.user,
        "tasks": Task.objects.filter(owner=request.user,selected=False,completion_date__isnull=True),
        "projects": Project.objects.filter(owner=request.user,completion_date__isnull=True),
        "impossible_project_id": impossible_project_id
        
    })

@login_required
# Route for daily view that shows reminders and tasks for the current day
def daily_view(request):
    return render(request, "tasks/daily.html",{
        "user": request.user,
        "tasks": Task.objects.filter(owner=request.user, selected=True).annotate(min=F("current_task_time")/60).annotate(sec=F("current_task_time")-F("current_task_time")/60*60),
        "reminders": Reminder.objects.filter(owner=request.user,reminder_date=date.today(),completion_date__isnull=True)
    })

# Route for logging in
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tasks/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tasks/login.html")

@login_required
# Route for logging out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
# Route for viewing tasks and reminders associated with a project
def project_view(request, project_id):

    try:
        project = Project.objects.get(pk=project_id)
        tasks = Task.objects.filter(project=project_id,owner=request.user, completion_date__isnull=True, selected=False)
        reminders = Reminder.objects.filter(project=project_id,owner=request.user, completion_date__isnull=True)

        #If successful query then render html for tasks and reminders with projects
        return render(request, "tasks/project_assigned.html",{
            "project": project,
            "tasks": tasks,
            "reminders": reminders
        })

    except Project.DoesNotExist:
        tasks = Task.objects.filter(owner=request.user, project__isnull=True, completion_date__isnull=True, selected=False)
        reminders = Reminder.objects.filter(owner=request.user, project__isnull=True, completion_date__isnull=True)

        #If successful query then render html for tasks and reminders with no projects
        return render(request, "tasks/no_project_assigned.html",{
            "tasks": tasks,
            "reminders": reminders
        })

# Route for registering an account
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "tasks/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "tasks/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tasks/register.html")

@login_required
# Route for completing tasks, reminders, projects
def complete(request):
    data_request_id = request.GET.get('id')
    data_request_type = request.GET.get('type')

    if data_request_type == 'task':

        # Complete task
        task = Task.objects.get(pk=data_request_id)
        task.completion_time = task.current_task_time
        task.selected = False
        task.completion_date = date.today()
        task.save()
        return HttpResponse(status=200)

    elif data_request_type == 'reminder':

        # Complete reminder
        reminder = Reminder.objects.get(pk=data_request_id)
        reminder.completion_date = date.today()
        reminder.save()
        return HttpResponse(status=200)
        
    elif data_request_type == 'project':

        # Complete project
        project = Project.objects.get(pk=data_request_id)
        project.completion_date = date.today()
        project.save()

        # Complete tasks
        tasks = Task.objects.filter(project=project)
        for task in tasks:
            task.completion_date = date.today()
            task.save()
        
        # Complete reminders
        reminders = Reminder.objects.filter(project=project)
        for reminder in reminders:
            reminder.completion_date = date.today()
            reminder.save()
        
        return HttpResponse(status=200)

@login_required
# Route for viewing completed tasks by date
def completedate(request, date):
    # Query task
    try:
        tasks = Task.objects.filter(owner=request.user,completion_date=date).annotate(min=F("completion_time")/60).annotate(sec=F("completion_time")-F("completion_time")/60*60)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    #If successful query then return route
    return render(request, "tasks/completedtasks.html",{
        "tasks": tasks
    })

@login_required
# Route to view completed tasks
def completed(request):
    return render(request, "tasks/complete.html",{
        "user": request.user,
        "summary": Task.objects.filter(owner=request.user).exclude(completion_date__isnull=True).values("completion_date").annotate(total=Count("completion_date")).order_by("-completion_date")
    })

@login_required
# Route for creating Reminders
def create(request):
    if request.method == "POST":
        
        # Save Form Type
        form_type = request.POST["formtype"]

        # Reminder Form
        if form_type == "reminder":

            # If a Project was selected then save project with reminder
            try:
                project = Project.objects.get(pk=request.POST["project"])
                project_id = project.id
                r = Reminder(
                    owner=request.user,
                    project=project,
                    description=request.POST["content"],
                    reminder_date=request.POST["reminder_date"]
                )
                r.save()
            
                # Route User back to Current Project view
                url = reverse("project",kwargs={'project_id': project_id})
                return HttpResponseRedirect(url)

            # If a Project was not selected then do not save a project associated with reminder
            except Project.DoesNotExist:
                r = Reminder(
                    owner=request.user,
                    description=request.POST["content"],
                    reminder_date=request.POST["reminder_date"]
                )
                r.save()

                # Generate kwargs with impossible project id
                max_project_id = Project.objects.all().order_by("-id")[0].id
                impossible_project_id = max_project_id+1

                # Route User back to viewing reminders with no projects
                url = reverse("project",kwargs={'project_id': impossible_project_id})
                return HttpResponseRedirect(url)

        # Task Form
        elif form_type == "task":

            # If a Project was selected then save project with task
            try:
                project = Project.objects.get(pk=request.POST["project"])
                project_id = project.id
                t = Task(
                    owner=request.user,
                    project=project,
                    description=request.POST["content"]
                )
                t.save()
                
                # Route User back to Current Project view
                url = reverse("project",kwargs={'project_id': project_id})
                return HttpResponseRedirect(url)

            # If a Project was not selected then do not save a project associated with task
            except Project.DoesNotExist:
                t = Task(
                    owner=request.user,
                    description=request.POST["content"]
                )
                t.save()

                # Generate kwargs with impossible project id
                max_project_id = Project.objects.all().order_by("-id")[0].id
                impossible_project_id = max_project_id+1

                # Route User back to viewing tasks with no projects
                url = reverse("project",kwargs={'project_id': impossible_project_id})
                return HttpResponseRedirect(url)

        # Project Form
        elif form_type == "project":

            # Ensure there are only 3 Projects Created // I removed constraint for having only 3 projects
            total_projects = Project.objects.filter(completion_date__isnull=True,owner=request.user).count()

            p = Project(
            owner=request.user,
            project_title=request.POST["title"],
            anticipated_completion_date=request.POST["anticipated_completion_date"]
            )
            p.save()
            return HttpResponseRedirect(reverse("backlog"))

@login_required
# Route to pause timer
def pause(request):
    data_request_id = request.GET.get('id')
    data_request_task_time = int(request.GET.get('current_task_time'))-1
    task = Task.objects.get(pk=data_request_id)
    task.current_task_time = data_request_task_time
    task.save()
    return HttpResponseRedirect(reverse("daily"))

@login_required
# Route for deleting tasks and reminders
def remove(request):        
    
    try:
        # Delete Task
        data_request_task_id = request.GET.get('task_id')
        task = Task.objects.get(pk=data_request_task_id)
        task.delete()
        return HttpResponse(status=200)

    except Task.DoesNotExist:
        # Delete Reminder
        data_request_reminder_id = request.GET.get('reminder_id')
        reminder = Reminder.objects.get(pk=data_request_reminder_id)
        reminder.delete()
        return HttpResponse(status=200)

@login_required
# Route for selecting and deselecting tasks
def select(request, task_id):
    if request.method == "PUT":
        # Query task
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)
        
        # Ensure task owner selected/deselected task
        if task.owner != request.user:
            return JsonResponse({"error": "Not allowed"}, status=403)
        
        # Select / Deselect tasks
        total_selected = Task.objects.filter(selected=True,owner=request.user).count()

        # Prevent more than three tasks from being selected
        if total_selected >= 3:
            if task.selected == False:
                return JsonResponse({"message": "You can only select 3 tasks!","error": 1}, status=200)
            else:
                task.selected = False
                task.save()
                return JsonResponse({"message": "We'll complete this another time","error": 0}, status=200)

        # Deselect task
        elif task.selected == True:
            task.selected = False
            task.save()
            return JsonResponse({"message": "We'll complete this another time","error": 0}, status=200)
        
        # Select task
        else:
            task.selected = True
            task.save()
            return JsonResponse({"message": "Nice selection, let's get to work!","error": 0}, status=200)

@login_required
# Route to start timer
def start(request):
    data_request = request.GET.get('id')
    task = Task.objects.get(pk=data_request)
    data = {
        'current_task_time': task.current_task_time
    }
    return JsonResponse(data)

def task_chart(request):
    labels = []
    data = []

    queryset = Task.objects.filter(owner=request.user).exclude(completion_date__isnull=True).values("completion_date").annotate(total_tasks=Count("completion_date")).order_by("completion_date")
    for entry in queryset:
        labels.append(entry['completion_date'])
        data.append(entry['total_tasks'])
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

def time_chart(request):
    labels = []
    data = []

    queryset = Task.objects.filter(owner=request.user).exclude(completion_date__isnull=True).values("completion_date").annotate(avg_task=Avg("completion_time")/60).order_by("completion_date")
    for entry in queryset:
        labels.append(entry['completion_date'])
        data.append(entry['avg_task'])
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })



