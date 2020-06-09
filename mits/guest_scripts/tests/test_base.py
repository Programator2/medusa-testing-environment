import inspect


class TestBase:
    """
    Class implements preparation logic behinds the scenes and is ready for
    inheritance. Classes, which inherit this class implements just tests.
    @ test_category - test category of a test suite (string)
    """
    test_category = None

    def __init__(self, shell_session):
        def _discover_tests():
            """
            Helper routine for test discovery, only tests which do not start
            with '_' are discovered.
            """
            methods = inspect.getmembers(self, predicate=inspect.ismethod)
            found_tests = []
            for name, func in methods:
                if not name.startswith("_"):
                    found_tests.append((name, func))
            return found_tests

        self.shell_session = shell_session
        self.tests = _discover_tests()

    def _suite_setup(self):
        return NotImplementedError()

    def _suite_cleanup(self):
        return NotImplementedError()
