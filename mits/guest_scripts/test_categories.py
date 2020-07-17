import os
import sh
from mits_enums import TestCategory
from errors import MountPointError, CleanupError


def lsm_setup(test_category_path, **kwargs):
    if os.path.exists(test_category_path):
        raise CleanupError("Testing path was not cleaned up")

    sh.mkdir(f'{test_category_path}')
    sh.mkdir(f'{test_category_path}/allowed')
    sh.mkdir(f'{test_category_path}/restricted')


def mounting_setup(test_category_path, **kwargs):
    if os.path.exists(test_category_path):
        raise CleanupError("Testing path was not cleaned up")

    available_partitions = kwargs['options']['mounting']['partitions']
    free_partition = _get_available_partition(available_partitions)

    sh.mkdir(f'{test_category_path}')
    sh.mount(free_partition, f'{test_category_path}', '-text4')
    sh.mkdir(f'{test_category_path}/allowed')
    sh.mkdir(f'{test_category_path}/restricted')


# TODO we need to solve a problem, what if someone wants to mount 3 partitions
# but only 2 are available, those 2 can be used for some other test category
# however right now the list will be empty after someone pulled 2 of them
def _get_available_partition(available_partitions):
    if available_partitions is not None and len(available_partitions) > 0:
        return available_partitions.pop()
    else:
        raise MountPointError("Guest: no available mount points")


setup_routines = {
        TestCategory.BASIC.value: lsm_setup,
        TestCategory.CREATION.value: lsm_setup,
        TestCategory.MOUNTING.value: mounting_setup
}
