class AnnotationError(Exception):
    """
    The error is used if unknown annotation was found in config file
    """
    pass


class MountPointError(Exception):
    """
    The error is used if there is no available mount points for mounting
    """
    pass

class CleanupError(Exception):
    """
    The error is used if the environment should be cleaned up but is not
    """
    pass
