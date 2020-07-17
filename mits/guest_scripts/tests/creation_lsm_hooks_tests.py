from mits_enums import ShellAnswer, TestCategory
from test_base import TestBase


class CreationLsmHooksTests(TestBase):
    test_categories = [TestCategory.CREATION.value, TestCategory.MOUNTING.value]
    config_filename = 'creation_lsm_hooks_tests'

    def mkdir_basic_allow(self):
        dir_to_create = 'allowed/mkdir_allow_test'
        result = self.shell_session.execute_cmd(f'mkdir {dir_to_create}')
        result.should_be_empty()

    def mkdir_basic_deny(self):
        dir_to_create = 'restricted/mkdir_denied_test'
        result = self.shell_session.execute_cmd(f'mkdir {dir_to_create}')
        result.should_contain(ShellAnswer.DENIED.value)

    def create_basic_allow(self):
        file_to_create = 'allowed/create.txt'
        result = self.shell_session.execute_cmd(f'touch {file_to_create}')
        result.should_be_empty()

    def create_basic_deny(self):
        file_to_create = 'restricted/create.txt'
        result = self.shell_session.execute_cmd(f'touch {file_to_create}')
        result.should_contain(ShellAnswer.DENIED.value)

    def mknod_basic_allow(self):
        pipe_to_create = 'allowed/fifo p'
        result = self.shell_session.execute_cmd(f'mknod {pipe_to_create}')
        result.should_be_empty()

    def mknod_basic_deny(self):
        pipe_to_create = 'restricted/fifo p'
        result = self.shell_session.execute_cmd(f'mknod {pipe_to_create}')
        result.should_contain(ShellAnswer.DENIED.value)

    def _test_setup(self, dest, dummy):
        self.shell_session.execute_cmd(f'mkdir {dest}/restricted/{dummy}')
        self.shell_session.execute_cmd(f'mkdir {dest}/allowed/{dummy}')
        self.shell_session.execute_cmd(f'ln -s {dest}/restricted/{dummy} restricted')
        self.shell_session.execute_cmd(f'ln -s {dest}/allowed/{dummy} allowed')
