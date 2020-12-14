// Initialize singlestart variable used to ensure only 1 start timer is used while user is on the page
var singlestart = 0;

// Upon DOM Load
document.addEventListener('DOMContentLoaded', function() {

    // For pages with the refresh input ensure they are 
    $(document).ready(function(e) {
        var $input = $('#refresh');

        $input.val() == 'yes' ? location.reload(true) : $input.val('yes');
    });

    // Initialize interval for timer counting
    var interval;
    
        // Set timer counter in local storage
        if (!localStorage.getItem('counter')){
            localStorage.setItem('counter',0);
        }

    // Complete Task, Reminder, Project. In the Daily View (Note that the Timer MUST be paused)
    document.querySelectorAll('.complete').forEach(complete => {
        complete.addEventListener('click', function() {
            
            // Set data type of the complete button (task, reminder, project)
            const datatype = complete.dataset.type

            if(datatype == 'task'){
             
                // Set taskId and element
                const element = event.target;
                const taskId = complete.dataset.task;

                // If Timer is still counting alert user to pause it
                if(singlestart == 1){
                    alert("Please stop all timers before completing a task!")
                }
                else {

                    // Pass task_id to the update route
                    $.ajax({
                        url: 'update',
                        data: {
                            'id': taskId,
                            'type': datatype
                        },
                        dataType: 'json'
                    });

                    // Remove the task from the Daily View
                    element.parentElement.parentElement.parentElement.remove();

                }
            }
            else if(datatype == 'reminder'){

                // Set reminderId and element
                const element = event.target;
                const reminderId = element.dataset.reminder;

                // Pass reminder_id to the update route
                $.ajax({
                    url: 'update',
                    data: {
                        'id': reminderId,
                        'type': datatype
                    },
                    dataType: 'json'
                });

                // Remove project
                element.parentElement.parentElement.remove();
                console.log(reminderId);
            }
            else if(datatype == 'project'){

                // Set projectId and element
                const element = event.target;
                const projectId = element.dataset.projectid;

                // Pass project_id to the update route
                $.ajax({
                    url: 'update',
                    data: {
                        'id': projectId,
                        'type': datatype
                    },
                    dataType: 'json'
                });

                // Remove project
                element.parentElement.parentElement.remove();
            }
        })
    });

    // Delete Task Or Reminders from Projects 
    document.querySelectorAll('.remove').forEach(remove => {
        remove.addEventListener('click', function() {
            
            // Set taskId, reminderId and element
            const element = event.target;
            const taskId = remove.dataset.task;
            const reminderId = remove.dataset.reminder;

            // Pass task_id and reminder_id to the remove route
            $.ajax({
                url: 'remove',
                data: {
                    'task_id': taskId,
                    'reminder_id': reminderId
                },
                dataType: 'json'
            });

            // Remove the Task or Reminder
            element.parentElement.parentElement.remove();
        })
    });

    // Pause Timer on a Task in the Daily View
    document.querySelectorAll('.pause').forEach(pause => {
        pause.addEventListener('click', function() {
            
            // Set current_task_time and clear the counter interval
            let current_task_time = localStorage.getItem('counter');
            clearInterval(interval);
            
            // Set taskId and element
            const element = event.target;
            const taskId = element.dataset.task;

            // Hide the pause button for the task
            $("#pause_"+taskId).hide()

            // Pass task_id to the pause route
            $.ajax({
                url: 'pause',
                data: {
                    'id': taskId,
                    'current_task_time': current_task_time
                },
                dataType: 'json'
            });

            // Set singlestart variable to 0 so that one timer can be started again
            singlestart--;

        })
    });

    // Select/Deselect Tasks for the Daily View
    document.querySelectorAll('.select').forEach(select => {
        select.addEventListener('click', function() {
            
            // Set taskId and element
            const element = event.target;
            const taskId = select.dataset.task;

            // Set token and fetch task select route
            const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            fetch(`/select/${taskId}`, {
                method: 'PUT',
                headers: {
                    "X-CSRFToken": token
                }
            })
            .then(response => response.json())
            .then(data => {
                
                // Alert user if more than 3 tasks have already been selected 
                if (data.error == 1){
                    alert(data.message)
                }
                
                // Otherwise send user Select / Deselect message 
                else{
                    // removed encouraging alert alert(data.message)
                    element.parentElement.parentElement.remove();
                }
            });
        })
    });

    // Start Timer on a Task in the Daily View 
    document.querySelectorAll('.start').forEach(start => {
        start.addEventListener('click', function() {

            // Ensure only one timer has been started
            if (singlestart == 1) {
                alert("You can only work one task at a time!")
            }

            // Otherwise start timer
            else{

                // Set taskId and element
                const element = event.target;
                const taskId = element.dataset.task;

                // Show pause button for task that was started
                $("#pause_"+taskId).show()

                // Pass task_id to the start route
                $.ajax({
                    url: 'start',
                    data: {
                        'id': taskId
                    },
                    dataType: 'json',
                    
                    // Receive current_task_time from Task model for task
                    success: function(data){
                        
                        // Set counter in local storage to the current_task_time
                        localStorage.setItem('counter',data.current_task_time);
                        
                        // Count function for timer
                        function count(input) {
                            
                            // Initialize Counter Variable and increase it
                            let counter = localStorage.getItem('counter');
                            counter++;
                            
                            // Calculate seconds and minutes using 
                            let seconds = localStorage.getItem('counter');
                            let minutes = Math.floor(localStorage.getItem('counter') / 60);
                            
                            // If more than 1 minute has passed
                            if(seconds > 60) {
                                seconds = seconds - 60*minutes;
                                document.querySelector(`#timer_${taskId}`).innerHTML = `${minutes} minute(s),${seconds} seconds`;
                            }
                            
                            // Otherwise 
                            else{
                                document.querySelector(`#timer_${taskId}`).innerHTML = `${minutes} minute(s),${seconds} seconds`;
                            }

                            // Set local storage counter to counter 
                            localStorage.setItem('counter', counter);
                        }
                        
                        // Set and run interval using count function 
                        interval = setInterval(count, 1000);
                    }
                });

                // Set singlestart variable to 1 so that no other timers can be started until current one is paused
                singlestart++;
            }
        })
    });
});
