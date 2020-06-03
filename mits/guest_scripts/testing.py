"""
@package mits.testing
This module executes tests and testing suites
"""
import os
import pickle
#import shlex
#import subprocess
#import threading
#import time
import sys
import tabulate

import commons
import config
from asynchronous_reader import Reader
from report import ResultsDirector
from mkdir_tests import MkdirTest
from local_shell import LocalShell


def test_director(pickle_location):
    """
    Unpickles tuple of tests and suites chosen by the user to be executed.
    Based on the selected tests, it creates configuration for Constable.
    @param pickle_location: File name of the pickled test information
    """

    def unpickle_tests(tests_path):
        """ Reads pickled tests from test_path, which were pickled by host system.
        @param tests_path: Full path to the pickled data file.
        @return: Pickled data. It should be tuple of lists containing names of the tests and suites, respectively.
        """
        with open(tests_path, 'rb') as f:
            return pickle.load(f, fix_imports=True)

    # Unpickle test information that was prepared by hosting computer
    (tests, suites) = unpickle_tests(os.path.join(commons.VM_MTE_PATH, pickle_location))
    print(f"Send tests are {tests}")
    # We need to create configuration file just once
    create_configuration(tests)
    for suite in suites:
        (results, outputs, outputs_denied) = start_suite(tests, suite)
        print_class_report(results)
        #print(f'Generating report for {suite}')
        #ResultsDirector.generate_results(results, outputs, outputs_denied, suite, commons.TESTING_PATH)

def print_class_report(results):
    headers = ['Test name', 'Is passed']
    rows = [(name, result) for name, result in results.items()]
    print(tabulate.tabulate(rows, headers=headers))


def start_suite(tests, suite_name):
    """
    Main testing function, starts Constable and executes tests one after the other. When
    all testing is done, results are sent to the validator module to be validated.
    @param tests: List of system calls to be tested and called
    @param suite_name: Name of the suite. Currently two types of suites are supported: sequential (do_tests)
    and concurrent (do_concurrent_tests)
    @return: Tuple of results and outputs. Outputs list is included only in concurrent suite, otherwise it's None.
    """
    local_shell = LocalShell()
    mkdir_tests = [ MkdirTest(local_shell) ]
    # clean dmesg before starting Constable
    #dmesg_before = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
    #                              stdout=subprocess.PIPE).stdout

    # TODO Decide what to do with dmesg_before (maybe filter it for medusa messages?)
    # start constable and save its standard output
    print('Starting Constable')
    constable = Reader('sudo constable ' + commons.TESTING_PATH + '/constable.conf')
    # Catch first outputs and save them independently to testing outputs

    time.sleep(1)
    print('Reading Constable')
    constable_start = constable.read()

    print('Running dmesg')
    #dmesg_start = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
    #                             stdout=subprocess.PIPE).stdout

    print('Starting test batch')
    (results, outputs, outputs_denied) = getattr(sys.modules[__name__], suite_name)(mkdir_tests, constable)

    print('Terminating Constable')
    constable.terminate()

    time.sleep(1)
    constable_end = constable.read()
    #dmesg_end = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
    #                           stdout=subprocess.PIPE).stdout
    # TODO Make room for additional information (dmesg_before, dmesg_start and both ends) in the report file
    return (results, outputs, outputs_denied)


def create_configuration(tests):
    """
    Creates and saves configuration file based on chosen system calls.
    @param tests: List of system calls to be executed during testing.
    """
    # create configuration file and save it
    configuration = config.make_config(tests)
    if not os.path.exists(commons.TESTING_PATH + '/restricted'):
        os.makedirs(commons.TESTING_PATH + '/restricted')
    # TODO Check if you can write into it
    print('Creating configuration')
    config_file = open(commons.TESTING_PATH + '/medusa.conf', 'w')
    config_file.write(configuration)
    config_file.close()
    # create constable configuration file that refers to medusa.conf
    config_file = open(commons.TESTING_PATH + '/constable.conf', 'w')
    config_file.write(config.constable_config)
    config_file.close()

def class_tests(test_classes, constable):
    results = {}
    for test_class in test_classes:
        tests = test_class.tests
        for test_name, test_case in tests.items():
            print(f'Executing test {test_name}: {test_case}')
            results[test_name] = str(test_case())

    return (results, None, None)

"""
For now it is not used, it will be removed later
"""
#def do_concurrent_tests(tests, constable):
#    """
#    Executes system calls enumerated in list concurrently (almost at the same time).
#    @param tests: List of system calls to be executed.
#    @param constable: Reader object of constable output.
#    @return: Tuple of results and outputs. Results is a dictionary containing dmesg and constable outputs.
#    Outputs is a list of dictionaries containing outputs of executed system calls.
#    These outputs should be ideally empty except for the fork system call.
#    """
#    # We should create a thread for each test command and lock it. After all tests are ready and constable is started,
#    # we release them. Now, there is a change in catching output from constable
#    outputs = []
#    outputs_denied = []
#    threads = []
#    # create a lock
#    lock = threading.Lock()
#    lock.acquire()
#    os.chdir(commons.TESTING_PATH)
#
#    def testing_thread(test):
#        lock.acquire()
#        lock.release()
#        os.chdir(commons.TESTING_PATH)
#        outputs.append({'test': test, 'output': execute_cmd(config.tests[test]['command'])})
#
#    def testing_thread_denied(test):
#        lock.acquire()
#        lock.release()
#        os.chdir(commons.TESTING_PATH)
#        outputs_denied.append({'test': test, 'output': execute_cmd(config.tests[test]['command_denied'])})
#
#    for test in tests:
#        new_thread = threading.Thread(name=test, target=testing_thread, args=[test])
#        if 'command_denied' in test:
#            denied_thread = threading.Thread(name=test, target=testing_thread_denied, args=[test])
#            threads.append(denied_thread)
#            denied_thread.start()
#        threads.append(new_thread)
#        new_thread.start()
#
#    lock.release()
#
#    for t in threads:
#        t.join()
#
#    system_log = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
#                                stdout=subprocess.PIPE).stdout
#    constable_out = constable.read()
#    results = {'output': 'Concurrent logs', 'system_log': system_log, 'constable': constable_out}
#    return results, outputs, outputs_denied


#def do_tests(tests, constable):
#    """ Executes commands in the list sequentially and returns their output with kernel log messages
#    @param tests: List of tests to be executed
#    @param constable: Handle of running Constable process
#    @return: List of dictionaries with two members: output and log
#    """
#    results = []
#    os.chdir(commons.TESTING_PATH)
#    for test in tests:
#        print('Executing test ' + test)
#        result = {}
#
#        cmd = config.tests[test]['command']
#        output = execute_cmd(cmd)
#        time.sleep(1)
#        system_log = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
#                                    stdout=subprocess.PIPE).stdout
#        constable_out = constable.read()
#        result['test'] = test
#        result['output'] = output
#        result['system_log'] = system_log
#        result['constable'] = constable_out
#
#        if 'command_denied' in config.tests[test]:
#            cmd = config.tests[test]['command_denied']
#            output_denied = execute_cmd(cmd)
#            time.sleep(1)
#            system_log_denied = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
#                                        stdout=subprocess.PIPE).stdout
#            constable_out_denied = constable.read()
#            result['output_denied'] = output_denied
#            result['system_log_denied'] = system_log_denied
#            result['constable_denied'] = constable_out_denied
#
#        results.append(result)
#    return results, None, None
#
#
#def prepare(tests):
#    """
#    Prepares testing folder according to 'before' action defined in the config module.
#    Before action can be None, a single string or a list of strings.
#    @param tests: List of tests to be executed.
#    """
#    os.chdir(commons.TESTING_PATH)
#    for test in tests:
#        if config.tests[test]['before'] is not None:
#            # TODO insert to list
#            if type(config.tests[test]['before']) is str:
#                execute_cmd(config.tests[test]['before'], config.tests[test]['before_async'])
#            elif type(config.tests[test]['before']) is list:
#                for cmd in config.tests[test]['before']:
#                    execute_cmd(cmd, config.tests[test]['before_async'])
#
#
#def do_cleanup(tests):
#    """
#    Executed the 'after' action defined in the config module.
#    Action is usually set to remove files created by tests
#    @param tests: Tests that were executed
#    """
#    for test in tests:
#        if config.tests[test]['after'] is not None:
#            execute_cmd(config.tests[test]['after'])

#def execute_cmd(cmd, is_async=False):
#    """ Executes command on the system and returns output
#    @param cmd: Command to be executed
#    @param async: If true, command will be executed asynchronously (function will not wait for it to end)
#    @return: Standard output of the executed command if executed synchronously, nothing if is_async=True
#    >>> execute_cmd('echo This is a test')
#    'This is a test\\n'
#    """
#    if (is_async):
#        execute_cmd_async(cmd)
#        return
#    process = subprocess.run(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE,
#                             stderr=subprocess.STDOUT)
#    return process.stdout
#
#def execute_cmd_async(cmd):
#    """ Executes command on the system without returning output
#    @param cmd: Command to be executed
#    """
#    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    test_director(sys.argv[1])
