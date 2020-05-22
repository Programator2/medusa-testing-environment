# -*- coding: utf-8 -*-
"""
@package mits.shell
Controls communication with a virtual machine through SSH protocol
"""
import hashlib
import os
import pickle
from socket import error

import paramiko
from scp import SCPClient

import commons


class Shell:
    def __init__(self, ip, port, username, password):
        """
        Creates a new SSH connection and determines prompt.
        @param ip: IP adress of a server to connect to.
        @param port: Port of the server to connect to.
        @param username: Username
        @param password: Password of the chosen user.
        @return: Shell object.
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


def connect(args):
    """
    Connects to a virtual machine and performs checks for a new version of
    Medusa. Afterwards it executes the testing batch.
    @param args: Tuple of two lists. First list contains names of system calls
    to be tested and second one contains name of the testing suites to be run.
    """
    try:
        ssh = Shell(commons.VM_IP, commons.VM_PORT, commons.USER_NAME,
                    commons.USER_PASSWORD)
    except error as e:
        print(e.args[1])
        exit(-1)
        return
    except paramiko.ssh_exception.AuthenticationException as e:
        print(e.message)
        exit(-1)
        return
    # Downloading new version from repository
    print('Checking for new version of Medusa (this may take a while)')
    ssh.exec_cmd('cd ' + commons.MEDUSA_PATH)
    git_result = ssh.exec_cmd('git pull')
    while True:
        if 'Already up to date.' in git_result:
            print('Medusa is up to date.')
            break
            # continue
        elif 'Updating' in git_result:
            print('Medusa was updated.')
            # assume that the newest kernel is automatically the default one
            compile_command = commons.MEDUSA_PATH + '/build.sh --noreboot'
            if commons.NO_GRUB:
                compile_command += ' --nogdb'
            if is_kernel_same(ssh):
                compile_command += ' --medusa-only'
            ssh.instant_cmd(compile_command)
            print('Kernel compiled')
            if is_sudo_active(ssh):
                ssh.channel.send('sudo reboot\n')
            else:
                ssh.channel.send('sudo reboot\n' + commons.USER_PASSWORD + '\n')
            ssh.close()
            print('Rebooting the system')
            return 1
            # TODO Don't save the output, it's too much
        elif 'Please, commmit your changes or stash them before you can merge.' in git_result:
            # TODO Make this selectable at the start of the script
            while True:
                choice = input('This will delete your local changes to Medusa. Do you want to continue? [y/N] ')\
                    .lower()
            if choice == 'y' or 'yes':
                break
            elif choice == '' or 'n' or 'no':
                ssh.close()
                exit()
            ssh.exec_cmd('git reset --hard HEAD')
            git_result = ssh.exec_cmd('git pull')
            continue
        elif 'fatal: unable to access' in git_result:
            print("Couldn't connect to git. Continuing with current version.")
            break
        else:
            raise RuntimeError('Unrecognized git response')
    # TODO add else for no Internet connection
    # Check if testing environment is located on VM. If not, copy it.
    upload_testing_suite(ssh, args)
    print('Start of testing procedure')
    # TODO Implement a bit safer version with sudo -k, with more attempts than just one and with better output control
    if is_sudo_active(ssh):
        print('Sudo is active, no need to input password')
        # Starting without sudo, need to adjust accordingly
        # TODO Change way of accessing sudo
        ssh.instant_cmd('sudo python3 ' + commons.VM_MTE_PATH + '/testing.py pickled_tests')
    else:
        # password = raw_input('Please enter your sudo password to continue: ')
        ssh.instant_cmd('sudo python3 ' + commons.VM_MTE_PATH + '/testing.py pickled_tests\n' + commons.USER_PASSWORD)
    print('End of testing procedure')
    transport_results(ssh, args[1])
    ssh.close()
    return 0


def transport_results(ssh, suites):
    """
    Downloads test results from virtual machine to the host.
    @param ssh: SSH connection to the virtual machine.
    @param suites: List of names of test suites that were executed.
    """
    scp = SCPClient(ssh.ssh.get_transport())
    scp.get(commons.TESTING_PATH + '/result_details', commons.OUTPUT_PATH, recursive=True)
    for suite in suites:
        scp.get(commons.TESTING_PATH + '/results_' + suite + '.html', commons.OUTPUT_PATH)
    scp.close()


def is_sudo_active(ssh):
    """
    Checks if sudo doesn't ask for password
    @param ssh: SSH connection
    @return: True if sudo works without password. False if sudo asks for password.
    """
    sudo = ssh.exec_cmd('sudo -n true 2>/dev/null && echo "True" || echo "False"')
    return 'True' in sudo
    # if sudo.find('True') != -1:
    #     return True
    # else:
    #     return False


def upload_testing_suite(ssh, tests):
    """
    Uploads files needed for testing. These are defined in files set.
    Also uploads pickled tests chosen by user in host system.
    @param ssh: SSH connection
    @param tests: Tuple of two lists. First list contains names of system calls to be tested and second one contains
     name of the testing suites to be run.
    """
    # Set current directory to a folder, where the running script is located
    # print os.path.realpath(__file__)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    scp = SCPClient(ssh.ssh.get_transport())
    # These files will be copied from host computer to guest
    files = {'guest_scripts/report.py', 'guest_scripts/asynchronous_reader.py',
             'commons.py', 'guest_scripts/testing.py',
             'config.py', 'guest_scripts/fork',
             'guest_scripts/validator.py'}
    path_exists = ssh.exec_cmd('[ -d ' + commons.VM_MTE_PATH + ' ] && echo "True" || echo "False"')
    if 'False' in path_exists:
        # create path if it doesn't exist and copy all files without checking diference
        # TODO What if the path is invalid?
        ssh.exec_cmd('mkdir -p ' + commons.VM_MTE_PATH)
        for f in files:
            scp.put(f, commons.VM_MTE_PATH, preserve_times=True)
    else:
        for f in files:
            file_exists = ssh.exec_cmd('[ -f ' + commons.VM_MTE_PATH + '/' + f + ' ] && echo "True" || echo "False"')
            if file_exists.find('True') != -1:
                local_hash = hashlib.md5(open(f, 'rb').read()).hexdigest()
                print(type(local_hash))
                remote_hash = ssh.exec_cmd('md5sum ' + commons.VM_MTE_PATH + '/' + f)
                if remote_hash.find(local_hash) == -1:
                    scp.put(f, commons.VM_MTE_PATH, preserve_times=True)
            else:
                scp.put(f, commons.VM_MTE_PATH, preserve_times=True)
    # Also upload pickled test names
    with open('pickled_tests', 'wb') as f:
        pickle.dump(tests, f)
    scp.put('pickled_tests', commons.VM_MTE_PATH, preserve_times=True)
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


def setup_virtual_pc():
    """
    Installs the pexpect module on the virtual machine, for the asynchronous reader to work.
    """
    try:
        ssh = Shell(commons.VM_IP, commons.VM_PORT, commons.USER_NAME, commons.USER_PASSWORD)
    except error as e:
        print(e.args[1])
        exit(-1)
        return
    except paramiko.ssh_exception.AuthenticationException as e:
        print(e.message)
        exit(-1)
        return
    ssh.instant_cmd('python3 -m pip install pexpect')
    # ssh.exec_cmd('sudo init 0')
    ssh.close()

# if __name__ == '__main__':
#     connect('test')
