from PySide2.QtWidgets import *
from habitipy import Habitipy, load_conf, DEFAULT_CONF
from enum import Enum

# global vars
tasks = []
widget_registry = {}


class TodoType(Enum):
    HABIT = 'habit'
    DAILY = 'daily'
    TODO = 'todo'
    REWARD = 'reward'

    def __str__(self):
        return self.value

# will mutate the tasks list passed in
def reload_tasks(api:Habitipy, tasks:list):
    new_tasks = load_tasks(api)
    tasks.clear()
    for new_task in new_tasks:
        tasks.append(new_task)
    return tasks

# Finds selected task ids from the global tasks for checked items.
def find_selected_task_id(widget_registry:dict) -> str:
    found = find_selected_task(widget_registry)
    if found is not None:
        return found.get('id', None)
    else:
        return None

# Finds selected task ids from the global tasks for checked items.
def find_selected_task(widget_registry:dict):
    item_group_tasks = widget_registry.get('item_group_tasks', None)
    if item_group_tasks is not None:
        # get selected
        for index, task in enumerate(item_group_tasks):
            if task.isChecked():
                task = tasks[index]
                return task
    return None

def add_button_cb(api:Habitipy, tasks:list, widget_registry:dict, text:str, textarea:str, priority:int):
    task_id = find_selected_task_id(widget_registry)
    priority_values = ['0.1', '1', '1.5', '2']
    api_priority = priority_values[priority]
    if task_id is None:
        api.tasks.user.post(text=text, type=str(TodoType.TODO), notes=textarea, priority=api_priority)
    else:
        api.tasks[task_id].put(text=text, type=str(TodoType.TODO), notes=textarea, priority=api_priority)
    clear_button_cb(api, widget_registry)

# Mark selected tasks as done
def save_button_cb(api:Habitipy, widget_registry:dict, tasks:list):
    task_id = find_selected_task_id(widget_registry)
    api.tasks[task_id].score['up'].post()
    clear_button_cb(api, widget_registry)

def edit_button_cb(api:Habitipy, widget_registry: dict):
    # FIXME: extract this
    priority_values = ['0.1', '1', '1.5', '2']
    task = find_selected_task(widget_registry)
    if task is None:
        print('no selected task found for edit') 
        return

    # set values in inputs
    add_input = widget_registry['task_input']
    add_input_textarea = widget_registry['task_textarea']
    priority_select = widget_registry['task_priority']
    add_input.setText(task.get('text', ''))
    add_input_textarea.setText(task.get('notes', ''))
    item_priority = priority_values.index(str(task.get('priority', 0)))
    priority_select.setCurrentIndex(item_priority)

# Delete selected tasks
def delete_button_cb(api:Habitipy, widget_registry:dict, tasks:list):
    task_id = find_selected_task_id(widget_registry)
    if task_id is None:
        print(f'No task id found {task_id}')
        return
    api.tasks[task_id].delete()
    clear_button_cb(api, widget_registry)

def checkbox_selected_cb(api, widget_registry:dict, selected:bool):
    if selected is False:
        return
    edit_button_cb(api, widget_registry)

def clear_button_cb(api:Habitipy, widget_registry:dict):
    task_input = widget_registry['task_input']
    task_input.clear()
    widget_registry['task_textarea'].clear()
    widget_registry['task_priority'].setCurrentIndex(0)
    reload_tasks(api, tasks)
    create_item_group(api, tasks, widget_registry)
    task_input.setFocus()

def load_tasks(api) -> list:
    # {'challenge': {}, 'group': {'approval': {'required': False, 'approved': False, 'requested': False},
    # 'assignedUsers': [], 'sharedCompletion': 'singleCompletion'}, 'completed': False, 'collapseChecklist': False,
    # 'type': 'todo', 'notes': None, 'tags': [], 'value': -44.17407706858991, 'priority': 2, 'attribute': 'str',
    # 'byHabitica': False, 'checklist': [], 'reminders': [], 'createdAt': '2020-03-15T05:51:17.040Z',
    # 'updatedAt': '2020-04-11T14:55:48.962Z', '_id': '4BF9CA59-FEDB-45B4-BE45-BCE58384A423', 'date': None,
    # 'text': 'Clean House', 'userId': 'e192efef-1de2-4ae6-9804-9bd4ab9b30b6',
    # 'id': '4BF9CA59-FEDB-45B4-BE45-BCE58384A423'}
    return api.tasks.user.get(type='todos')

def create_action_group(api:Habitipy, widget_registry:dict, tasks:list):
    group = QGroupBox('Actions')
    layout = QHBoxLayout()

    # save
    save_button = QPushButton('Mark Done')
    save_button.clicked.connect(lambda: save_button_cb(api, widget_registry, tasks))

    # delete
    delete_button = QPushButton('Delete')
    delete_button.clicked.connect(lambda: delete_button_cb(api, widget_registry, tasks))

    layout.addWidget(save_button)
    layout.addWidget(delete_button)
    group.setLayout(layout)
    return (group, layout)

def create_input_action_group(api:Habitipy, widget_registry:dict, tasks:list, add_input, add_input_textarea, priority_select):
    group = QGroupBox('Input Actions')
    layout = QHBoxLayout()

    # add button
    add_button = QPushButton('Add')
    add_button.clicked.connect(lambda: add_button_cb(api, tasks, widget_registry, add_input.text(), add_input_textarea.toPlainText(), priority_select.currentIndex()))

    # clear button
    clear_button = QPushButton('Clear')
    clear_button.clicked.connect(lambda: clear_button_cb(api, widget_registry))

    layout.addWidget(add_button)
    layout.addWidget(clear_button)
    group.setLayout(layout)
    return (group, layout)

def create_item_group(api:Habitipy, tasks:list, widget_registry:dict):
    item_group = widget_registry.get('item_group', None)
    item_group_layout = widget_registry.get('item_group_layout', None)
    item_group_tasks = widget_registry.get('item_group_tasks', None)

    if item_group is None:
        item_group = QGroupBox('Tasks')
        item_group_layout = QVBoxLayout()
        item_group_tasks = []
        item_group.setLayout(item_group_layout)
        widget_registry['item_group'] = item_group
        widget_registry['item_group_layout'] = item_group_layout
        widget_registry['item_group_tasks'] = item_group_tasks
    else:
        for task in item_group_tasks:
            item_group_layout.removeWidget(task)
            task.setParent(None)
        widget_registry['item_group_tasks'].clear()

    if tasks is not None:
        for task in tasks:
            checkbox = QRadioButton(task['text'])
            checkbox.toggled.connect(lambda selected: checkbox_selected_cb(api, widget_registry, selected))
            widget_registry['item_group_tasks'].append(checkbox)
            item_group_layout.addWidget(checkbox)

    return (item_group, item_group_layout)

def add_spacer(layout):
    # w, h
    vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding) 
    layout.addSpacerItem(vertical_spacer)
    return layout


# habitipy
api = Habitipy(load_conf(DEFAULT_CONF))
reload_tasks(api, tasks)

# app
app = QApplication([])
layout = QVBoxLayout()

# title
title = QLabel('Todo List')

# add
add_task_group = QGroupBox('Input')
add_task_group_layout = QVBoxLayout()
add_input = QLineEdit()
add_input_textarea = QTextEdit()
priority_select = QComboBox()
priority_select.addItem('Trivial')
priority_select.addItem('Easy')
priority_select.addItem('Medium')
priority_select.addItem('Hard')

widget_registry['task_input'] = add_input
widget_registry['task_textarea'] = add_input_textarea
widget_registry['task_priority'] = priority_select

add_task_group_layout.addWidget(add_input)
add_task_group_layout.addWidget(add_input_textarea)
add_task_group_layout.addWidget(priority_select)
add_task_group.setLayout(add_task_group_layout)

# action group
action_group, action_group_layout = create_action_group(api, widget_registry, tasks)

# input action group
input_action_group, input_action_group_layout = create_input_action_group(api, widget_registry, tasks, add_input, add_input_textarea, priority_select)

# items
item_group, item_group_layout = create_item_group(api, tasks, widget_registry)
widget_registry['item_group'] = item_group
widget_registry['item_group_layout'] = item_group_layout

# layout
layout.addWidget(title)
layout.addWidget(add_task_group)
layout.addWidget(input_action_group)
layout.addWidget(item_group)
layout.addWidget(action_group)

window = QWidget()
window.setLayout(layout)
# window.resize(600, 600)
window.show()
app.exec_()

# Signals:
# message.returnPressed.connect(send_message)
# timer = QTimer()
# timer.timeout.connect(display_new_messages)
# timer.start(1000)
# return app
