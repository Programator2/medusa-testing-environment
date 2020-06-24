# -*- coding: utf-8 -*-
"""
@package mits.remote_shell
Controls communication with a virtual machine through SSH protocol
"""
import hashlib
import os
import pickle
import paramiko

from glob import glob
from socket import error
from logger import log_host
from scp import SCPClient


class RemoteShell:
    def __init__(self, ip, port, username, password):
        """
        Creates a new SSH connection and determines prompt.
        @param ip: IP adress of a server to connect to.
        @param port: Port of the server to connect to.
        @param username: Username
        @param password: Password of the chosen user.
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ip, port=port, username=username, password=password)
        self.channel = self.ssh.invoke_shell()
        channel_data = ""
        while True:
            if self.channel.recv_ready():
                channel_data += self.channel.recv(9999).decode()
            else:
                continue
            if channel_data.endswith("$ ") or channel_data.endswith("# "):
                index = channel_data.rindex('\n')
                self.prompt = channel_data[index+1:]
                self.set_prompt()
                break

    def set_prompt(self):
        """
        Sets the prompt of a running SSH connetion to '[TPM]$ ' for easier
        recognition of an end of a command.
        """
        channel_data = ""
        sent = False
        while True:
            if not sent:
                self.channel.send('PS1="[TPM]\$ "\n')
                self.prompt = '[TPM]$ '
                sent = True
                channel_data = ""
            if self.channel.recv_ready():
                channel_data += self.channel.recv(9999).decode()
            else:
                continue
            if channel_data.endswith(self.prompt):
                break

    def exec_cmd(self, command):
        """
        Executes a command on the running SSH shell
        @param command: Command to execute
        @return: Full output of the command
        """
        channel_data = ""
        sent = False
        while True:
            if not sent:
                self.channel.send(command + '\n')
                sent = True
                channel_data = ""
            if self.channel.recv_ready():
                channel_data += self.channel.recv(9999).decode()
            else:
                continue
            if channel_data.endswith(self.prompt):
                return channel_data[len(command)+2:-len(self.prompt)]

    def instant_cmd(self, command):
        """
        Executes command and prints immediate output on the standard output.
        @param command: Command to execute
        @return: Full output of the command
        """
        channel_data = ""
        sent = False
        # Number of characters that needs to be cut before actual output begins
        cut = len(command)+2
        while True:
            if not sent:
                self.channel.send(command + '\n')
                sent = True
                channel_data = ""
            if self.channel.recv_ready():
                new_data = self.channel.recv(9999).decode()
                if 0 < cut < len(new_data):
                    # We have enough material to cut
                    new_data = new_data[cut:]
                    # print "Cutting " + cut + "characters"
                    cut = 0
                elif cut >= len(new_data):
                    # Cut everything
                    cut -= len(new_data)
                    new_data = ''
                channel_data += new_data
                # TODO Detect ending prompt and stop it from being shown. For
                # this we will have to wait until a newline
                # TODO comes and then we can decide if we want to print it or not.
                if new_data.find('[TPM]$ ') == -1 and new_data != '':
                    print(new_data)
            else:
                continue
            if channel_data.endswith(self.prompt):
                return channel_data[:-len(self.prompt)]

    def close(self):
        """
        Close the connection
        """
        self.channel.close()
        self.ssh.close()


def create_session(conn_info):
    """
    Connects to a virtual machine
    @conn_info: (dict) connection info for connection to guest machine
    @returns created ssh session or error message otherwise
    """
    try:
        return RemoteShell(conn_info['ip'], conn_info['port'],
                           conn_info['username'], conn_info['password'])
    except error as e:
        log_host(e.args[1])
        exit(-1)
    except paramiko.ssh_exception.AuthenticationException as e:
        log_host(e.message)
        exit(-1)


def pull_latest_git_version(ssh, medusa_conf, user_password):
    """
    Downloading new version of Medusa from repository and performs checks for
    a new version of Medusa. Afterwards it executes the testing batch.
    @param ssh: ssh session
    @param medusa_conf: (tuple) medusa path and built options
    @param user_password: (str) password of the logged user on guest machine
    """
    medusa_path, include_grub = medusa_conf.values()
    log_host('Checking for new version of Medusa (this may take a while)')
    ssh.exec_cmd('cd ' + medusa_path)
    git_result = ssh.exec_cmd('git pull')
    while True:
        if 'Already up to date.' in git_result:
            log_host('Medusa is up to date.')
            break
            # continue
        elif 'Updating' in git_result:
            log_host('Medusa was updated.')
            # assume that the newest kernel is automatically the default one
            compile_command = medusa_path + '/build.sh --noreboot'
            if include_grub is False:
                compile_command += ' --nogdb'
            if is_kernel_same(ssh):
                compile_command += ' --medusa-only'
            ssh.instant_cmd(compile_command)
            log_host('Kernel compiled')
            if is_sudo_active(ssh):
                ssh.channel.send('sudo reboot\n')
            else:
                ssh.channel.send('sudo reboot\n' + user_password + '\n')
            ssh.close()
            log_host('Rebooting the system')
            return 1
            # TODO Don't save the output, it's too much
        elif 'fatal: unable to access' in git_result:
            log_host("Couldn't connect to git. Continuing with current version.")
            break
        else:
            raise RuntimeError('Unrecognized git response')


def start_testing(ssh, exec_category, test_scripts_path, authserver):
    """
    Give control from the shell to the guest machine, so it can start the test
    execution. After the execution is done, fetch the results from testing back
    @param ssh: ssh session instance
    @param exec_category: execution category to be executed
    @param test_scripts_path: path, where the scripts are located on guest
    machine
    @param: authserver: (str) the authserver name, with which the testing
    should be executed
    """
    # TODO add else for no Internet connection
    # Check if testing environment is located on VM. If not, copy it.
    upload_testing_suite(ssh, exec_category, test_scripts_path, authserver)
    ssh.exec_cmd(f"cd {test_scripts_path}")
    log_host('Start of testing procedure')
    # TODO Implement a bit safer version with sudo -k, with more attempts than just one and with better output control
    if is_sudo_active(ssh):
        log_host('Sudo is active, no need to input password')
        ssh.instant_cmd(f'sudo python3 main.py pickled_exec_category')
    else:
        raise Exception("Host: The Sudo needs to be active")
    log_host('End of testing procedure')
    # transport_results(ssh, args[1])
    ssh.close()
    return 0


# def transport_results(ssh, suites):
#     """
#     Downloads test results from virtual machine to the host.
#     @param ssh: SSH connection to the virtual machine.
#     @param suites: List of names of test suites that were executed.
#     """
#     scp = SCPClient(ssh.ssh.get_transport())
#     scp.get(commons.TESTING_PATH + '/result_details', commons.OUTPUT_PATH, recursive=True)
#     for suite in suites:
#         scp.get(commons.TESTING_PATH + '/results_' + suite + '.html', commons.OUTPUT_PATH)
#     scp.close()


def is_sudo_active(ssh):
    """
    Checks if sudo doesn't ask for password
    @param ssh: SSH connection
    @return: True if sudo works without password. False if sudo asks for password.
    """
    sudo = ssh.exec_cmd('sudo -n true 2>/dev/null && echo "True" || echo "False"')
    return 'True' in sudo


def upload_testing_suite(ssh, exec_category, test_scripts_path, authserver):
    """
    Uploads files needed for testing. These are defined in files set.
    Also uploads pickled exec_category chosen by user in host system.
    @param ssh: SSH connection
    @param exec_category: execution category to be executed on guest machine
    @param test_scripts_path: (str) path, where the scripts are located on
    guest machine
    @param: authserver: (str) the authserver name, with which the testing
    should be executed
    @returns name of the uploaded file
    """
    # Set current directory to a folder, where the running script is located
    # print os.path.realpath(__file__)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    scp = SCPClient(ssh.ssh.get_transport())

    # These files will be copied from host computer to guest
    guest_files = glob('guest_scripts/*py')
    guest_files.extend(glob('guest_scripts/tests/*py'))
    guest_files.extend(glob('guest_scripts/*bin'))
    guest_files.extend(glob(f'guest_scripts/configs/{authserver}/*'))
    guest_files.extend(glob('guest_scripts/*yaml'))
    common_files = ['logger.py']
    files = guest_files + common_files
    log_host(f"Transferred files {files}")

    path_exists_expression = f'[ -d {test_scripts_path} ] && echo "True" || echo "False"'
    path_exists = ssh.exec_cmd(path_exists_expression)
    if path_exists == 'False':
        # create path if it doesn't exist and copy all files without checking diference
        # TODO What if the path is invalid?
        ssh.exec_cmd(f'mkdir -p {test_scripts_path}')
        for f in files:
            scp.put(f, test_scripts_path, preserve_times=True)
    else:
        for f in files:
            file_exists = ssh.exec_cmd(f'[ -f {test_scripts_path}/{f} ] && echo "True" || echo "False"')
            if file_exists.find('True') != -1:
                local_hash = hashlib.md5(open(f, 'rb').read()).hexdigest()
                remote_hash = ssh.exec_cmd(f'md5sum {test_scripts_path}/{f}')
                if remote_hash.find(local_hash) == -1:
                    scp.put(f, test_scripts_path, preserve_times=True)
            else:
                scp.put(f, test_scripts_path, preserve_times=True)
    # Also upload pickled test names
    with open('pickled_exec_category', 'wb') as f:
        pickle.dump(exec_category, f)
    scp.put('pickled_exec_category', test_scripts_path, preserve_times=True)
    scp.close()


def is_kernel_same(ssh):
    """
    Checks if kernel changed during git update.
    @param ssh: SSH connection
    @return: True if kernel didn't change. False if kernel changed.
    """
    new = ssh.exec_cmd('make kernelversion')
    running = ssh.exec_cmd('uname -r')
    return running.startswith(new)


def setup_virtual_pc(conn_info):
    """
    Installs the pexpect module on the virtual machine, for the asynchronous reader to work.
    @conn_info: (dict) connection info for connection to guest machine
    """
    ssh = create_session(conn_info)
    ssh.instant_cmd('python3 -m pip install pexpect')
    ssh.close()
