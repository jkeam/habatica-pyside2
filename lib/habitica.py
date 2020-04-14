from .task import TaskType, Priority, Task

class Habitica:
    def __init__(self, api):
        self.api = api
    
    def save(self, task_id:str, text:str, textarea:str, priority_index:int):
        if task_id is None:
            self.api.tasks.user.post(text=text, type=str(TaskType.TODO), notes=textarea, priority=Priority.priority_index_to_value(priority_index))
        else:
            self.api.tasks[task_id].put(text=text, type=str(TaskType.TODO), notes=textarea, priority=Priority.priority_index_to_value(priority_index))

    def mark_completed(self, task_id:str):
        self.api.tasks[task_id].score['up'].post()
    
    def destroy(self, task_id:str):
        self.api.tasks[task_id].delete()

    # {'challenge': {}, 'group': {'approval': {'required': False, 'approved': False, 'requested': False},
    # 'assignedUsers': [], 'sharedCompletion': 'singleCompletion'}, 'completed': False, 'collapseChecklist': False,
    # 'type': 'todo', 'notes': None, 'tags': [], 'value': -44.17407706858991, 'priority': 2, 'attribute': 'str',
    # 'byHabitica': False, 'checklist': [], 'reminders': [], 'createdAt': '2020-03-15T05:51:17.040Z',
    # 'updatedAt': '2020-04-11T14:55:48.962Z', '_id': '4BF9CA59-FEDB-45B4-BE45-BCE58384A423', 'date': None,
    # 'text': 'Clean House', 'userId': 'e192efef-1de2-4ae6-9804-9bd4ab9b30b6',
    # 'id': '4BF9CA59-FEDB-45B4-BE45-BCE58384A423'}
    def get_tasks(self):
        tasks = self.api.tasks.user.get(type='todos')
        def create_task(api_task):
            task = Task()
            task.id = api_task.get('id', None)
            task.text = api_task.get('text', '')
            task.notes = api_task.get('notes', '')
            task.priority = str(api_task.get('priority', '0.1'))
            return task
        return list(map(create_task, tasks))