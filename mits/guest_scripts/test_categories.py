import os
import sh
from mits_enums import TestCategory


def creation_setup(test_category_path, **kwargs):
    if os.path.exists(test_category_path):
        raise Exception("Testing path was not cleaned up")

    sh.mkdir(f'{test_category_path}')
    sh.mkdir(f'{test_category_path}/allowed')
    sh.mkdir(f'{test_category_path}/restricted')


def basic_workflows_setup(test_category_path, **kwargs):
    if os.path.exists(test_category_path):
        raise Exception("Testing path was not cleaned up")

    sh.mkdir(f'{test_category_path}')
    sh.mkdir(f'{test_category_path}/allowed')
    sh.mkdir(f'{test_category_path}/restricted')


def mounting_setup(test_category_path, **kwargs):
    if os.path.exists(test_category_path):
        raise Exception("Testing path was not cleaned up")

    sh.mount(f'{test_category_path}')
    sh.mkdir(f'{test_category_path}/allowed')
    sh.mkdir(f'{test_category_path}/restricted')


setup_routines = {
        TestCategory.BASIC.value: basic_workflows_setup,
        TestCategory.CREATION.value: creation_setup
}
