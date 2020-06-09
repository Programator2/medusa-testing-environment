from basic_lsm_hooks_tests import Basic_Lsm_Hooks_Tests
from creation_lsm_hooks_tests import Creation_Lsm_Hooks_Tests
from local_shell import LocalShell
from logger import log_guest
from mits_enums import ExecutionCategory
from commons import TESTING_PATH


registered_suites = {}


def register_suites():
    """
    Function registers all test classes from which the tests can be executed
    """
    def register_test_suite(test_suite, execution_category):
        test_class = test_suite.__class__.__name__.lower()
        is_registered = test_class in registered_suites.keys()
        if is_registered is False:
            log_guest(f"Registering {test_class}")
            registered_suites.setdefault(execution_category, []) \
                .append(test_suite)
        else:
            raise Exception("Guest: Test Class is already registered")

    shell = LocalShell(TESTING_PATH)

    # CI
    register_test_suite(Basic_Lsm_Hooks_Tests(shell), ExecutionCategory.CI.value)
    register_test_suite(Creation_Lsm_Hooks_Tests(shell), ExecutionCategory.CI.value)

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
        raise ValueError(f"Guest: no tests registered for {execution_category}")

    test_suites = {}
    for test_suite in registered_suites.get(execution_category, None):
        test_category = test_suite.test_category
        test_suites.setdefault(test_category, []).append(test_suite)

    return test_suites
