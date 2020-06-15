from enum import Enum
from errors import AnnotationError
import re


annotation_mappings = {
}


class ConfigAnnotation(Enum):
    TEST_ENV = '@{TEST_ENV}'


def annotation_init(config):
    annotation_mappings[ConfigAnnotation.TEST_ENV.value] = config['test_env']


def inject_paths(config):
    return _inject_paths(config, annotation_mappings)


def _inject_paths(config, annotation_mappings):
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
        mapped_string = annotation_mappings.get(annotation, None)
        if mapped_string is None:
            raise AnnotationError("Guest: unknown annotation found")
        return mapped_string

    def get_distinct_annotations(config_text):
        """
        Helper function for finding annotations inside config
        @param config_text - text where annotations are searched
        @returns found distinct annotations
        """
        annotation_pattern = '@{[A-Za-z_]+}'
        return set(re.findall(annotation_pattern, config_text))

    if isinstance(config, str) is False:
        raise ValueError('Guest: None config received')

    found_annotations = get_distinct_annotations(config)
    for annotation in found_annotations:
        path = map_annotation_to_path(annotation)
        config = config.replace(annotation, path)

    return config
