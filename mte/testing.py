"""@package mte.testing
This module executes tests and testing suites
"""
import os
import pickle
import shlex
import subprocess
import sys
import threading
import time

import commons
import config
from asynchronous_reader import Reader
from report import ResultsDirector
from validator import Validator


def test_director(pickle_location):
    """ Unpickles tuple of tests and suites chosen by the user to be executed.
    Based on the selected tests, it creates configuration for Constable.
    @param pickle_location: File name of the pickled test information
    """
    # Unpickle test information that was prepared by hosting computer
    (tests, suites) = unpickle_tests(os.path.join(commons.VM_MTE_PATH, pickle_location))
    # We need to create configuration file just once
    create_configuration(tests)
    for suite in suites:
        (results, outputs) = start_suite(tests, suite)
        (results, outputs) = Validator.validate(results, outputs)
        print('Generating report for ' + suite)
        ResultsDirector.generate_results(results, outputs, suite, commons.TESTING_PATH)


def start_suite(tests, suite_name):
    """ Main testing function, starts Constable and executes tests one after the other. When
    all testing is done, results are sent to the validator module to be validated.
    @param tests: List of system calls to be tested and called
    @param suite_name: Name of the suite. Currently two types of suites are supported: sequential (do_tests)
    and concurrent (do_concurrent_tests)
    @return: Tuple of results and outputs. Outputs list is included only in concurrent suite, otherwise it's None.
    """
    # clean dmesg before starting Constable
    dmesg_before = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
                                  stdout=subprocess.PIPE).stdout
    # TODO Decide what to do with dmesg_before (maybe filter it for medusa messages?)
    # execute 'before' part of tests written in config file
    prepare(tests)
    # start constable and save its standard output
    print('Starting Constable')
    constable = Reader('sudo constable ' + commons.TESTING_PATH + '/constable.conf')
    # Catch first outputs and save them independently to testing outputs
    time.sleep(1)
    print('Reading Constable')
    constable_start = constable.read()
    print('Running dmesg')
    dmesg_start = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
                                 stdout=subprocess.PIPE).stdout
    # start testing
    print('Starting test batch')
    (results, outputs) = getattr(sys.modules[__name__], suite_name)(tests, constable)
    # end constable
    print('Terminating Constable')
    constable.terminate()
    time.sleep(1)
    constable_end = constable.read()
    dmesg_end = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
                               stdout=subprocess.PIPE).stdout
    # TODO Make room for additional information (dmesg_before, dmesg_start and both ends) in the report file
    do_cleanup(tests)
    return (results, outputs)


def create_configuration(tests):
    """ Creates and saves configuration file based on chosen system calls.
    @param tests: List of system calls to be executed during testing.
    """
    # create configuration file and save it
    configuration = config.make_config(tests)
    if not os.path.exists(commons.TESTING_PATH):
        os.makedirs(commons.TESTING_PATH)
    # TODO Check if you can write into it
    print('Creating configuration')
    config_file = open(commons.TESTING_PATH + '/medusa.conf', 'w')
    config_file.write(configuration)
    config_file.close()
    # create constable configuration file that refers to medusa.conf
    config_file = open(commons.TESTING_PATH + '/constable.conf', 'w')
    config_file.write(config.constable_config)
    config_file.close()


def do_concurrent_tests(tests, constable):
    """ Executes system calls enumerated in list concurrently (almost at the same time).
    @param tests: List of system calls to be executed.
    @param constable: Reader object of constable output.
    @return: Tuple of results and outputs. Results is a dictionary containing dmesg and constable outputs.
    Outputs is a list of dictionaries containing outputs of executed system calls.
    These outputs should be ideally empty except for the fork system call.
    """
    # We should create a thread for each test command and lock it. After all tests are ready and constable is started,
    # we release them. Now, there is a change in catching output from constable
    outputs = []
    threads = []
    # create a lock
    lock = threading.Lock()
    lock.acquire()
    os.chdir(commons.TESTING_PATH)

    def testing_thread(test):
        lock.acquire()
        lock.release()
        os.chdir(commons.TESTING_PATH)
        outputs.append({'test': test, 'output': execute_cmd(config.tests[test]['command'])})

    for test in tests:
        new_thread = threading.Thread(name=test, target=testing_thread, args=[test])
        threads.append(new_thread)
        new_thread.start()

    lock.release()

    for t in threads:
        t.join()

    system_log = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
                                stdout=subprocess.PIPE).stdout
    constable_out = constable.read()
    results = {'output': 'Concurrent logs', 'system_log': system_log, 'constable': constable_out}
    return results, outputs


def do_tests(tests, constable):
    """ Executes commands in the list sequentially and returns their output with kernel log messages
    @param tests: List of tests to be executed
    @param constable: Handle of running Constable process
    @return: List of dictionaries with two members: output and log
    """
    results = []
    os.chdir(commons.TESTING_PATH)
    for test in tests:
        print('Executing test ' + test)
        cmd = config.tests[test]['command']
        output = execute_cmd(cmd)
        time.sleep(1)
        system_log = subprocess.run(shlex.split('sudo dmesg -ce'), universal_newlines=True,
                                    stdout=subprocess.PIPE).stdout
        constable_out = constable.read()
        results.append({'test': test, 'output': output, 'system_log': system_log, 'constable': constable_out})
    return results, None


def prepare(tests):
    """
    Prepares testing folder according to 'before' action defined in the config module.
    Before action can be None, a single string or a list of strings.
    @param tests: List of tests to be executed.
    """
    os.chdir(commons.TESTING_PATH)
    for test in tests:
        if config.tests[test]['before'] is not None:
            # insert to list
            if type(config.tests[test]['before']) is str:
                execute_cmd_async(config.tests[test]['before'])
            elif type(config.tests[test]['before']) is list:
                for cmd in config.tests[test]['before']:
                    execute_cmd_async(cmd)


def do_cleanup(tests):
    """
    Executed the 'after' action defined in the config module.
    Action is usually set to remove files created by tests
    @param tests: Tests that were executed
    """
    for test in tests:
        if config.tests[test]['after'] is not None:
            execute_cmd(config.tests[test]['after'])


def execute_cmd(cmd):
    """ Executes command on the system and returns output
    @param cmd: Command to be executed
    @return: Standard output of the executed command
    >>> execute_cmd('echo This is a test')
    'This is a test\\n'
    """
    process = subprocess.run(shlex.split(cmd), universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    return process.stdout


def execute_cmd_async(cmd):
    """ Executes command on the system without returning output
    @param cmd: Command to be executed
    """
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL)


def unpickle_tests(tests_path):
    """ Reads pickled tests from test_path, which were pickled by host system.
    @param tests_path: Full path to the pickled data file.
    @return: Pickled data. It should be tuple of lists containing names of the tests and suites, respectively.
    """
    with open(tests_path, 'rb') as f:
        return pickle.load(f, fix_imports=True)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    test_director(sys.argv[1])
