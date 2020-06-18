from mits_enums import ShellAnswer, TestCategory
from test_base import TestBase


class Basic_Lsm_Hooks_Tests(TestBase):
    test_category = TestCategory.BASIC.value

    def symlink_basic_creation_allow(self):
        example_text_file = 'allowed/symlink_allow_example_file.txt'
        setup_cmd = f"echo 'This is symlink test' > {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        symlink_file = 'allowed/symlink.ln'
        action_cmd = f'ln -s {example_text_file} {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return result is ShellAnswer.EMPTY.value

    def symlink_basic_creation_deny(self):
        example_text_file = 'restricted/link_allow_example_file.txt'
        setup_cmd = f"echo 'This is symlink test' > {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        symlink_file = 'restricted/link.ln'
        action_cmd = f'ln -s {example_text_file} {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.DENIED.value in result

    def link_basic_creation_allow(self):
        example_text_file = 'allowed/link_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        symlink_file = 'allowed/link.ln'
        action_cmd = f'ln {example_text_file} {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return result is ShellAnswer.EMPTY.value

    def link_basic_creation_deny(self):
        example_text_file = 'restricted/link_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        symlink_file = 'restricted/link.ln'
        action_cmd = f'ln {example_text_file} {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.DENIED.value in result

    def readlink_basic_allow(self):
        example_text_file = 'allowed/link_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)
        symlink_file = 'allowed/link.ln'
        create_symlink_cmd = f'ln -s {example_text_file} {symlink_file}'
        self.shell_session.execute_cmd(create_symlink_cmd)

        action_cmd = f'ls {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return symlink_file in result

    def readlink_basic_deny(self):
        example_text_file = 'restricted/readlink_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        symlink_file = 'restricted/readlink.ln'
        create_symlink_cmd = f'ln -s {example_text_file} {symlink_file}'
        self.shell_session.execute_cmd(create_symlink_cmd)

        action_cmd = f'ls {symlink_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.NOENT.value in result

    def rmdir_basic_allow(self):
        self.shell_session.execute_cmd('mkdir allowed/rmdir_test')

        action_cmd = 'rmdir allowed/rmdir_test'
        result = self.shell_session.execute_cmd(action_cmd)
        return result is ShellAnswer.EMPTY.value

    def rmdir_basic_deny(self):
        self.shell_session.execute_cmd('mkdir restricted/rmdir_test')

        action_cmd = 'rmdir restricted/rmdir_test'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.DENIED.value in result

    def unlink_basic_allow(self):
        example_text_file = 'allowed/unlink_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        action_cmd = f'unlink {example_text_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return result is ShellAnswer.EMPTY.value

    def unlink_basic_deny(self):
        example_text_file = 'restricted/unlink_allow_example_file.txt'
        setup_cmd = f"touch {example_text_file}"
        self.shell_session.execute_cmd(setup_cmd)

        action_cmd = f'unlink {example_text_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.DENIED.value in result

    def rename_basic_allow(self):
        old_file = 'allowed/rename_old.txt'
        setup_cmd = f"touch {old_file}"
        self.shell_session.execute_cmd(setup_cmd)

        new_file = 'allowed/rename_new.txt'
        action_cmd = f'mv {old_file} {new_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return result is ShellAnswer.EMPTY.value

    def rename_basic_deny(self):
        old_file = 'restricted/rename_old.txt'
        setup_cmd = f"touch {old_file}"
        self.shell_session.execute_cmd(setup_cmd)

        new_file = 'restricted/rename_new.txt'
        action_cmd = f'mv {old_file} {new_file}'
        result = self.shell_session.execute_cmd(action_cmd)
        return ShellAnswer.DENIED.value in result

    def _test_setup(self, target, dummy):
        self.shell_session.execute_cmd(f'mkdir {target}/restricted/{dummy}')
        self.shell_session.execute_cmd(f'mkdir {target}/allowed/{dummy}')
        self.shell_session.execute_cmd(f'ln -s {target}/restricted/{dummy} restricted')
        self.shell_session.execute_cmd(f'ln -s {target}/allowed/{dummy} allowed')
