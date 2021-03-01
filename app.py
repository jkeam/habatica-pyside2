import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from habitipy import Habitipy, load_conf, DEFAULT_CONF
from lib.task import TaskType, Task, Priority
from lib.widget_registry import WidgetRegistry, WidgetRegistryName
from lib.habitica import Habitica
from dotenv import load_dotenv
from os import getenv
from platform import system
load_dotenv()

# global vars
tasks = []
widget_registry = WidgetRegistry()

# will mutate the tasks list passed in
def reload_tasks(api:Habitica, tasks:list):
    new_tasks = api.get_tasks()
    tasks.clear()
    for new_task in new_tasks:
        tasks.append(new_task)
    return tasks

def find_selected_task_id(widget_registry:dict, tasks:list) -> str:
    found = find_selected_task(widget_registry, tasks)
    if found is not None:
        return found.id
    else:
        return None

# Finds selected task ids from the global tasks for checked items.
def find_selected_task(widget_registry:dict, tasks:list):
    item_group_tasks = widget_registry.retrieve(WidgetRegistryName.ITEM_GROUP_TASKS)
    if item_group_tasks is not None:
        # get selected
        for index, task in enumerate(item_group_tasks):
            if task.isChecked():
                task = tasks[index]
                return task
    return None

# Add new task
def add_button_cb(api:Habitica, tasks:list, widget_registry:dict, text:str, textarea:str, priority:int):
    task_id = find_selected_task_id(widget_registry, tasks)
    api.save(task_id, text, textarea, priority)
    clear_button_cb(api, widget_registry)

# Mark selected tasks as done
def save_button_cb(api:Habitipy, widget_registry:dict, tasks:list):
    task_id = find_selected_task_id(widget_registry, tasks)
    api.mark_completed(task_id)
    clear_button_cb(api, widget_registry)

# View the selected task
def view_selected_task(api:Habitipy, widget_registry: dict, tasks:list):
    task = find_selected_task(widget_registry, tasks)
    if task is None:
        print('no selected task found for edit')
        return

    # set values in inputs
    task_input = widget_registry.retrieve(WidgetRegistryName.TASK_INPUT)
    task_input_textarea = widget_registry.retrieve(WidgetRegistryName.TASK_TEXTAREA)
    priority_select = widget_registry.retrieve(WidgetRegistryName.TASK_PRIORITY)
    task_input.setText(task.text)
    task_input_textarea.setText(task.notes)
    priority_select.setCurrentIndex(Priority.priority_value_to_index(task.priority))
    widget_registry.retrieve(WidgetRegistryName.SAVE_BUTTON).setText('Update')

# Delete selected tasks
def delete_button_cb(api:Habitica, widget_registry:dict, tasks:list):
    task_id = find_selected_task_id(widget_registry, tasks)
    if task_id is None:
        print(f'No task id found {task_id}')
        return
    api.destroy(task_id)
    clear_button_cb(api, widget_registry)

# Fired when checkbox/radio is selected
def checkbox_selected_cb(api:Habitica, widget_registry:dict, tasks:list, selected:bool):
    if selected is False:
        clear_button_cb(api, widget_registry)
        return
    view_selected_task(api, widget_registry, tasks)

# Clear all inputs
def clear_button_cb(api:Habitica, widget_registry:dict):
    task_input = widget_registry.retrieve(WidgetRegistryName.TASK_INPUT)
    task_input.clear()
    widget_registry.retrieve(WidgetRegistryName.TASK_TEXTAREA).clear()
    widget_registry.retrieve(WidgetRegistryName.TASK_PRIORITY).setCurrentIndex(0)
    widget_registry.retrieve(WidgetRegistryName.SAVE_BUTTON).setText('Add')
    reload_tasks(api, tasks)
    create_item_group(api, tasks, widget_registry)
    task_input.setFocus()

def create_action_group(api:Habitica, widget_registry:dict, tasks:list):
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

def create_input_action_group(api:Habitica, widget_registry:dict, tasks:list):
    add_input = widget_registry.retrieve(WidgetRegistryName.TASK_INPUT)
    add_input_textarea = widget_registry.retrieve(WidgetRegistryName.TASK_TEXTAREA)
    priority_select = widget_registry.retrieve(WidgetRegistryName.TASK_PRIORITY)

    group = QGroupBox('Input Actions')
    layout = QHBoxLayout()

    # add button
    add_button = QPushButton('Add')
    add_button.clicked.connect(lambda: add_button_cb(api, tasks, widget_registry, add_input.text(), add_input_textarea.toPlainText(), priority_select.currentIndex()))
    widget_registry.store(WidgetRegistryName.SAVE_BUTTON, add_button)

    # clear button
    clear_button = QPushButton('Clear')
    clear_button.clicked.connect(lambda: clear_button_cb(api, widget_registry))

    layout.addWidget(add_button)
    layout.addWidget(clear_button)
    group.setLayout(layout)
    return (group, layout)

def create_item_group(api:Habitica, tasks:list, widget_registry:dict):
    item_group = widget_registry.retrieve(WidgetRegistryName.ITEM_GROUP)
    item_group_layout = widget_registry.retrieve(WidgetRegistryName.ITEM_GROUP_LAYOUT)
    item_group_tasks = widget_registry.retrieve(WidgetRegistryName.ITEM_GROUP_TASKS)

    if item_group is None:
        item_group = QGroupBox('Tasks')
        item_group_layout = QVBoxLayout()
        item_group_tasks = []
        item_group.setLayout(item_group_layout)
        widget_registry.store(WidgetRegistryName.ITEM_GROUP, item_group)
        widget_registry.store(WidgetRegistryName.ITEM_GROUP_LAYOUT, item_group_layout)
        widget_registry.store(WidgetRegistryName.ITEM_GROUP_TASKS, item_group_tasks)
    else:
        for task in item_group_tasks:
            item_group_layout.removeWidget(task)
            task.setParent(None)
        item_group_tasks.clear()

    if tasks is not None:
        for task in tasks:
            checkbox = QRadioButton(task.text)
            checkbox.toggled.connect(lambda selected: checkbox_selected_cb(api, widget_registry, tasks, selected))
            item_group_tasks = widget_registry.retrieve(WidgetRegistryName.ITEM_GROUP_TASKS)
            item_group_tasks.append(checkbox)
            item_group_layout.addWidget(checkbox)

    return (item_group, item_group_layout)

def create_task_action_group(api:Habitica, widget_registry: WidgetRegistry):
    add_task_group = QGroupBox('Input')
    add_task_group_layout = QVBoxLayout()
    add_input = QLineEdit()
    add_input_textarea = QTextEdit()
    priority_select = QComboBox()
    priority_select.addItem('Trivial')
    priority_select.addItem('Easy')
    priority_select.addItem('Medium')
    priority_select.addItem('Hard')

    widget_registry.store(WidgetRegistryName.TASK_INPUT, add_input)
    widget_registry.store(WidgetRegistryName.TASK_TEXTAREA, add_input_textarea)
    widget_registry.store(WidgetRegistryName.TASK_PRIORITY, priority_select)

    add_task_group_layout.addWidget(add_input)
    add_task_group_layout.addWidget(add_input_textarea)
    add_task_group_layout.addWidget(priority_select)
    add_task_group.setLayout(add_task_group_layout)
    return (add_task_group, add_task_group_layout)

def create_api():
    if system().lower() != 'windows':
        return Habitica(Habitipy(load_conf(DEFAULT_CONF)))

    config = {}
    config['url'] = getenv('URL', 'https://habitica.com')
    config['show_numbers'] = getenv('SHOW_NUMBERS', 'y')
    config['show_style'] = getenv('SHOW_STYLE', 'wide')
    config['login'] = getenv('LOGIN')
    config['password'] = getenv('PASSWORD')
    return Habitica(Habitipy(config))

try:
    # habitipy
    app = QApplication([])
    api = create_api()
    reload_tasks(api, tasks)

    # components
    title = QLabel('Todo List')
    add_task_group, add_task_group_layout = create_task_action_group(api, widget_registry)
    input_action_group, input_action_group_layout = create_input_action_group(api, widget_registry, tasks)
    action_group, action_group_layout = create_action_group(api, widget_registry, tasks)

    # items
    item_group, item_group_layout = create_item_group(api, tasks, widget_registry)
    widget_registry.store(WidgetRegistryName.ITEM_GROUP, item_group)
    widget_registry.store(WidgetRegistryName.ITEM_GROUP_LAYOUT, item_group_layout)

    # app and layout
    layout = QGridLayout()
    layout.addWidget(title, 0, 0)

    layout.addWidget(item_group, 1, 0)
    layout.addWidget(action_group, 2, 0)

    layout.addWidget(add_task_group, 1, 1)
    layout.addWidget(input_action_group, 2, 1)

    window = QWidget()
    window.setLayout(layout)
    # window.resize(600, 600)
    window.setWindowTitle('Habitica Todo')
    window.setWindowIcon(QIcon('lib/habitica.png'))
    window.show()
    app.exec_()
except:
    print(f'Unexpected error: {sys.exc_info()[0]}')
