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
        #@param async: If true, command will be executed asynchronously (function will not wait for it to end)
        #if (is_async):
        #    self.execute_cmd_async(cmd)
        #    return
        process = subprocess.run(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
        return process.stdout

    #def execute_cmd_async(self, cmd):
    #    """ Executes command on the system without returning output
    #    @param cmd: Command to be executed
    #    """
    #    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL)
