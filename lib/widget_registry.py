from enum import Enum

class WidgetRegistryName(Enum):
    ITEM_GROUP_TASKS = 'item_group_tasks'
    TASK_INPUT = 'task_input'
    TASK_TEXTAREA = 'task_textarea'
    TASK_PRIORITY = 'task_priority'
    ITEM_GROUP = 'item_group'
    ITEM_GROUP_LAYOUT = 'item_group_layout'

class WidgetRegistry:
    def __init__(self):
        self.registry = {}

    def store(self, key, value):
        self.registry[key] = value
        return self

    def retrieve(self, key, default=None):
        return self.registry.get(key, default)
