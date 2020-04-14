from enum import Enum

class Priority:
    @staticmethod
    def priority_index_to_value(index):
        priority_values = ['0.1', '1', '1.5', '2']
        return priority_values[index]

    @staticmethod
    def priority_value_to_index(value):
        priority_values = ['0.1', '1', '1.5', '2']
        return priority_values.index(value)

class TaskType(Enum):
    HABIT = 'habit'
    DAILY = 'daily'
    TODO = 'todo'
    REWARD = 'reward'

    def __str__(self):
        return self.value

class Task:
    def __init__(self):
        self.id = None
        self.text = ''
        self.notes = ''
        self.priority = ''