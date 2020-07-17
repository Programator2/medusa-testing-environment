import shlex
import subprocess


class LocalShell:
    def execute_cmd(self, cmd):
        """ Executes command on the system and returns output
        @param cmd: Command to be executed
        @return: Standard output of the executed command if executed synchronously, nothing if is_async=True
        >>> execute_cmd('echo This is a test')
        'This is a test\\n'
        """
        if not isinstance(cmd, str):
            raise TypeError("Guest: expected command")
        elif not cmd:
            raise ValueError("Guest: command cannot be empty")

        process = subprocess.run(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        return process.stdout
