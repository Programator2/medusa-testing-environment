from mits_enums import ShellAnswer, TestCategory
from test_base import TestBase

class Creation_Lsm_Hooks_Tests(TestBase):
    test_categories = [TestCategory.CREATION.value]

    def mkdir_basic_allow(self):
        dir_to_create = 'allowed/mkdir_allow_test'
        result = self.shell_session.execute_cmd(f'mkdir {dir_to_create}')
        return result is ShellAnswer.EMPTY.value

    def mkdir_basic_deny(self):
        dir_to_create = 'restricted/mkdir_denied_test'
        result = self.shell_session.execute_cmd(f'mkdir {dir_to_create}')
        return ShellAnswer.DENIED.value in result

    def create_basic_allow(self):
        file_to_create = 'allowed/create.txt'
        result = self.shell_session.execute_cmd(f'touch {file_to_create}')
        return result is ShellAnswer.EMPTY.value

    def create_basic_deny(self):
        file_to_create = 'restricted/create.txt'
        result = self.shell_session.execute_cmd(f'touch {file_to_create}')
        return ShellAnswer.DENIED.value in result

    def mknod_basic_allow(self):
        pipe_to_create = 'allowed/fifo p'
        result = self.shell_session.execute_cmd(f'mknod {pipe_to_create}')
        return result is ShellAnswer.EMPTY.value

    def mknod_basic_deny(self):
        pipe_to_create = 'restricted/fifo p'
        result = self.shell_session.execute_cmd(f'mknod {pipe_to_create}')
        return ShellAnswer.DENIED.value in result

    def _test_setup(self, target, dummy):
        self.shell_session.execute_cmd(f'mkdir {target}/restricted/{dummy}')
        self.shell_session.execute_cmd(f'mkdir {target}/allowed/{dummy}')
        self.shell_session.execute_cmd(f'ln -s {target}/restricted/{dummy} restricted')
        self.shell_session.execute_cmd(f'ln -s {target}/allowed/{dummy} allowed')
