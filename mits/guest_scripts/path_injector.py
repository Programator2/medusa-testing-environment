from enum import Enum
from commons import TESTING_PATH, VM_MTE_PATH
from errors import AnnotationError
from logger import log_guest
import re


class ConfigAnnotation(Enum):
    TEST_ENV = '@{TEST_ENV}'
    TEST_SCRIPTS = '@{TEST_SCRIPTS}'


def inject_paths(config):
    """
    Function replaces the found annotations inside config with path
    @param config - configuration text content as string
    @returns config with injected path
    """
    def map_annotation_to_path(annotation):
        """
        Helper function makes mapping from annotation to path
        @param annotation - found annotation in config file
        @returns mapped path as str or AnnotationError
        """
        mapped_string = annotation_mappings.get(annotation, '')
        if not mapped_string:
            raise AnnotationError(f"Guest: unknown annotation {annotation}")
        return mapped_string

    def get_distinct_annotations(config_text):
        """
        Helper function for finding annotations inside config
        @param config_text - text where annotations are searched
        @returns found distinct annotations
        """
        annotation_pattern = '@{[A-Za-z_]+}'
        return set(re.findall(annotation_pattern, config_text))

    found_annotations = get_distinct_annotations(config)
    for annotation in found_annotations:
        path = map_annotation_to_path(annotation)
        config = config.replace(annotation, path)

    return config


if not __name__ == '__main__':
    annotation_mappings = {
            ConfigAnnotation.TEST_ENV.value: TESTING_PATH,
            ConfigAnnotation.TEST_SCRIPTS.value: VM_MTE_PATH
            }
