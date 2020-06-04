from shell_answers import ShellAnswer


class MkdirTests:
    def __init__(self, ssh_session):
        self.tests = {
            'mkdir_allow': self.mkdir_allow,
            'mkdir_deny': self.mkdir_deny
        }
        self.ssh_session = ssh_session

    def mkdir_allow(self):
        """
        Test for basic mkdir allow
        """
        dir_to_create = 'mkdir_allow_test'
        result = self.ssh_session.execute_cmd(f'mkdir {dir_to_create}')
        self.cleanup(dir_to_create)
        return result in ShellAnswer.EMPTY.value

    def mkdir_deny(self):
        """
        Test for basic mkdir deny
        """
        dir_to_create = 'restricted/mkdir_denied_test'
        result = self.ssh_session.execute_cmd(f'mkdir {dir_to_create}')
        self.cleanup(dir_to_create)
        return result in ShellAnswer.DENIED.value

    def cleanup(self, dir_name):
        self.ssh_session.execute_cmd(f'rmdir {dir_name}')
