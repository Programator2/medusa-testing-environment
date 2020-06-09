from enum import Enum


class ShellAnswer(Enum):
    EMPTY = ''
    DENIED = 'Permission denied'
    NOENT = 'No such file or directory'


class ExecutionCategory(Enum):
    CI = 'CI'
    REGRESSION = 'Regression'
    OFFSTREAM = 'Offstream'


class TestCategory(Enum):
    BASIC = 'basic_workflow'
    CREATION = 'creation'
