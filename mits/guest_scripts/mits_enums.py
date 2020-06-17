from enum import Enum


class ShellAnswer(Enum):
    """
    """
    EMPTY = ''
    DENIED = 'Permission denied'
    NOENT = 'No such file or directory'


class ExecutionCategory(Enum):
    """
    @CI - stands for 'Continuous integration' and is used to run tests, which did
    not enter 'Regression' execution category yet
    """
    CI = 'CI'

    """
    @Regression execution category is used for stable tests, which covers stable
    features in Medusa (eg. system calls, which were developed a long time ago)
    """
    REGRESSION = 'Regression'

    """
    @Offstream execution category is used for test coverage of features, which
    cannot enter the upstream branch
    """
    OFFSTREAM = 'Offstream'


class TestCategory(Enum):
    """
    @BASIC - basic allow/deny/not found tests
    """
    BASIC = 'basic_workflow'

    """
    @CREATION - tests which checks whether the files/folders/pipes were
    created successfully.
    """
    CREATION = 'creation'
