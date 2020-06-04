from mkdir_tests import MkdirTests
from local_shell import LocalShell
from logger import log_guest


registered_suites = {}


def register_suites():
    """
    Function registers all test classes from which the tests can be executed
    """
    def register_test_suite(test_suite):
        test_class = test_suite.__class__.__name__.lower()
        is_registered = test_class in registered_suites.keys()
        if (not is_registered):
            log_guest(f"Registering {test_class}")
            registered_suites[test_class] = test_suite
        else:
            raise Exception("Guest: Test Class is already registered")

    shell = LocalShell()
    register_test_suite(MkdirTests(shell))


def get_test_classes_from(test_suites):
    """
    The function retrieves test classes based on provided test class names
    @param test_suites - list of test class names
    """
    test_classes = []
    for name, test_class in registered_suites.items():
        if name in test_suites:
            test_classes.append(test_class)
    return test_classes


def contains_all_suites(test_suites):
    return set(test_suites).issubset(registered_suites.keys())
