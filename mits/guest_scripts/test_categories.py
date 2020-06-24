import os
from mits_enums import TestCategory


def creation_setup(test_env_path):
    if not os.path.exists(test_env_path):
        raise Exception("Testing path not found")

    os.mkdir(f'{test_env_path}/allowed')
    os.mkdir(f'{test_env_path}/restricted')


def basic_workflows_setup(test_category_path):
    if not os.path.exists(test_category_path):
        raise Exception("Testing path not found")

    os.mkdir(f'{test_category_path}/allowed')
    os.mkdir(f'{test_category_path}/restricted')


setup_routines = {
        TestCategory.BASIC.value: basic_workflows_setup,
        TestCategory.CREATION.value: creation_setup
}
