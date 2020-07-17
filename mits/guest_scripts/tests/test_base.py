import inspect
import should_be.all


class TestBase:
    """
    Class implements preparation logic behinds the scenes and is ready for
    inheritance. Classes, which inherit this class implements just tests.
    @test_categories - test categories to which test suite belongs (list)
    """
    test_categories = None
    config_filename = None

    def __init__(self, shell_session):
        def _discover_tests():
            """
            Helper routine for test discovery, only tests which do not start
            with '_' are discovered.
            """
            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            found_tests = []
            for name, func in methods:
                if not name.startswith("_") and not name.startswith("should"):
                    found_tests.append((name, func))
            return found_tests

        self.shell_session = shell_session
        self.tests = _discover_tests()

    def _test_setup(self):
        return NotImplementedError()
