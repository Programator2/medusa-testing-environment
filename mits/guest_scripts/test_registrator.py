from basic_lsm_hooks_tests import BasicLsmHooksTests
from creation_lsm_hooks_tests import CreationLsmHooksTests
from local_shell import LocalShell
from logger import log_guest
from mits_enums import ExecutionCategory


registered_suites = {}


def register_suites():
    """
    Function registers all test classes from which the tests can be executed
    """
    def register_test_suite(test_suite, execution_category):
        """
        Registration subroutine for registering test_suite for provided exec.
        category
        @param test_suite: test suite instance to be registered
        @paran execution_category: execution category for test suite
        @Exception is raised if the test suite is registered already
        """
        test_class = test_suite.__class__.__name__.lower()
        is_registered = test_class in registered_suites.keys()
        if is_registered is False:
            log_guest(f"Registering {test_class}")
            registered_suites.setdefault(execution_category, []) \
                .append(test_suite)
        else:
            raise Exception("Guest: Test suite is already registered")

    shell = LocalShell()

    # CI
    register_test_suite(BasicLsmHooksTests(shell), ExecutionCategory.CI.value)
    register_test_suite(CreationLsmHooksTests(shell), ExecutionCategory.CI.value)

    # Regression

    # Offstream


def get_test_suites_for(execution_category):
    """
    The function retrieves test suites based on provided execution category
    @param execution_category - the name of execution category, for which the
    tests should be executed
    @returns the dictionary of test suites, where key is test category and
    value is list of related test suites
    """
    suites_to_run = registered_suites.get(execution_category, None)
    if suites_to_run is None:
        raise ValueError("Guest: no tests registered for given category")

    test_suites = {}
    for test_suite in registered_suites.get(execution_category, None):
        for test_category in test_suite.test_categories:
            test_suites.setdefault(test_category, []).append(test_suite)

    return test_suites
