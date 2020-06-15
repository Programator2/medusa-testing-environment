import shlex
import subprocess


class LocalShell:
    def execute_cmd(self, cmd, is_async=False):
        """ Executes command on the system and returns output
        @param cmd: Command to be executed
        @return: Standard output of the executed command if executed synchronously, nothing if is_async=True
        >>> execute_cmd('echo This is a test')
        'This is a test\\n'
        """
        process = subprocess.run(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        return process.stdout
