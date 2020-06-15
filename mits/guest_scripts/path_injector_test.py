import unittest
import path_injector as PathInjector
from errors import AnnotationError


class PathInjectorTest(unittest.TestCase):
    def test_inject_paths_empty(self):
        content = ''
        result = PathInjector.inject_paths(content)
        self.assertEqual(result, content)

    def test_inject_paths_simple_string(self):
        content = 'hello there'
        result = PathInjector.inject_paths(content)
        self.assertEqual(result, content)

    def test_inject_paths_none_handled(self):
        with self.assertRaises(ValueError):
            PathInjector.inject_paths(None)
            PathInjector.inject_paths(5)

    def test_inject_paths_simple_annotation_found(self):
        content = '@{TEST_ENV}'
        annotations = {}
        annotations[content] = "ANOTHER PATH"
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "ANOTHER PATH")

    def test_inject_paths_simple_annotation_begin_surrounded(self):
        annotation = '@{TEST_ENV}'
        annotations = {}
        annotations[annotation] = "ANOTHER PATH"
        content = "abc" + annotation

        result = PathInjector._inject_paths(content, annotations)

        self.assertEqual(result, "abcANOTHER PATH")

    def test_inject_paths_simple_annotation_end_surrounded(self):
        annotation = '@{TEST_ENV}'
        annotations = {}
        annotations[annotation] = "ANOTHER PATH"
        content = annotation + "abc"

        result = PathInjector._inject_paths(content, annotations)

        self.assertEqual(result, "ANOTHER PATHabc")

    def test_inject_paths_simple_annotation_fully_surrounded(self):
        annotation = '@{TEST_ENV}'
        annotations = {}
        annotations[annotation] = "ANOTHER PATH"
        content = "bcd" + annotation + "abc"

        result = PathInjector._inject_paths(content, annotations)

        self.assertEqual(result, "bcdANOTHER PATHabc")

    def test_inject_paths_simple_nested_annotation_supported(self):
        annotation = '@{TEST_ENV}'
        annotations = {}
        annotations[annotation] = "ANOTHER PATH"

        content = '@{@{TEST_ENV}}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "@{ANOTHER PATH}")

    def test_inject_paths_one_annotation_multiple_times_in_config(self):
        annotation = '@{TEST_ENV}'
        annotations = {}
        annotations[annotation] = "ANOTHER PATH"

        content = '@{TEST_ENV}@{TEST_ENV}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "ANOTHER PATHANOTHER PATH")

    def test_inject_paths_multiple_annotations(self):
        annotation = ['@{TEST_ENV}', '@{SCRIPTS}']
        annotations = {}
        annotations[annotation[0]] = "ANOTHER PATH"
        annotations[annotation[1]] = "SCRIPTS PATH"

        content = '@{TEST_ENV} @{SCRIPTS} @{TEST_ENV}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "ANOTHER PATH SCRIPTS PATH ANOTHER PATH")

    def test_inject_paths_replaced_annotation_expanded(self):
        annotation = ['@{TEST_ENV}', '@{SCRIPTS}']
        annotations = {}
        annotations[annotation[0]] = "ANOTHER PATH"
        annotations[annotation[1]] = "@{TEST_ENV}"

        content = '@{TEST_ENV} @{SCRIPTS} @{TEST_ENV}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "ANOTHER PATH ANOTHER PATH ANOTHER PATH")

    def test_inject_paths_replaced_annotation_expanded_in_any_order(self):
        annotation = ['@{TEST_ENV}', '@{SCRIPTS}']
        annotations = {}
        annotations[annotation[0]] = "@{SCRIPTS}"
        annotations[annotation[1]] = "SCRIPTS PATH"

        content = '@{TEST_ENV} @{SCRIPTS} @{TEST_ENV}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "SCRIPTS PATH SCRIPTS PATH SCRIPTS PATH")

    def test_inject_paths_multi_annotation_expansion(self):
        annotation = ['@{TEST_ENV}', '@{SCRIPTS}', '@{SOME_OTHER}']
        annotations = {}
        annotations[annotation[0]] = "@{SOME_OTHER}"
        annotations[annotation[1]] = "@{TEST_ENV}"
        annotations[annotation[2]] = "PATH"

        content = '@{TEST_ENV} @{SCRIPTS} @{TEST_ENV}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "PATH PATH PATH")

    def test_inject_paths_simple_cycle_detected(self):
        annotation = ['@{TEST_ENV}', '@{SCRIPTS}', '@{NON_TERMINAL}']
        annotations = {}
        annotations[annotation[0]] = "@{SCRIPTS}"
        annotations[annotation[1]] = "SCRIPTS PATH"
        annotations[annotation[2]] = "@{NON_TERMINAL}"

        content = '@{TEST_ENV} @{SCRIPTS} @{NON_TERMINAL}'
        result = PathInjector._inject_paths(content, annotations)
        self.assertEqual(result, "SCRIPTS PATH SCRIPTS PATH @{NON_TERMINAL}")
