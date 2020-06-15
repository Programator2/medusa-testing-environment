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
    Function replaces the found annotations inside config with path. The
    function supports also smaller cycle detection of length 1.
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

    def expand_annotation(config, annotation):
        """
        Helper function for expanding the provided annotation to it's mapping
        @param config: the configuration file content, where annotations should
        be replaced
        @param annotation: annotation to be replaced with path
        @return new config with expanded annotation to path
        """
        path = map_annotation_to_path(annotation)
        return config.replace(annotation, path)

    if not isinstance(config, str):
        raise ValueError('Guest: None config received')

    old_config = None
    while config != old_config:
        found_annotations = get_distinct_annotations(config)
        old_config = config
        for annotation in found_annotations:
            config = expand_annotation(config, annotation)
    return config
