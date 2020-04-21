from .task import TaskType, Priority, Task

class Habitica:
    """ Habatica functionality """
    def __init__(self, api):
        self.api = api
   
    def save(self, task_id: str, text: str, textarea: str, priority_index: int):
        """ Save task """
        if task_id is None:
            self.api.tasks.user.post(text=text, type=str(TaskType.TODO), notes=textarea, priority=Priority.priority_index_to_value(priority_index))
        else:
            self.api.tasks[task_id].put(text=text, type=str(TaskType.TODO), notes=textarea, priority=Priority.priority_index_to_value(priority_index))

    def mark_completed(self, task_id: str):
        """ Mark task as completed """
        self.api.tasks[task_id].score['up'].post()
    
    def destroy(self, task_id: str):
        """ Destroy task """
        self.api.tasks[task_id].delete()

    def get_tasks(self):
        """ Get tasks """
        tasks = self.api.tasks.user.get(type='todos')
        def create_task(api_task):
            task = Task()
            task.id = api_task.get('id', None)
            task.text = api_task.get('text', '')
            task.notes = api_task.get('notes', '')
            task.priority = str(api_task.get('priority', '0.1'))
            return task
        return list(map(create_task, tasks))
