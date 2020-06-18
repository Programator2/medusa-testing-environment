"""
@package mits.testing
This module executes tests and testing suites
"""
import os
import pickle
import time
import sys
import yaml
import tabulate
import test_registrator as TestRegistrator
from asynchronous_reader import Reader
from logger import log_guest
from local_shell import LocalShell
import uuid
import test_settings
import path_injector as PathInjector


def unpickle_tests(tests_path):
    """
    Reads pickled tests from test_path, which were pickled by host system.
    @param tests_path: Full path to the pickled data file.
    @return: Pickled data. It should be tuple of lists containing names of
    the tests and suites, respectively.
    """
    with open(tests_path, 'rb') as f:
        return pickle.load(f, fix_imports=True)


def init():
    with open("subconfig.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.Loader)

    test_settings.init(config['settings'])
    TestRegistrator.register_suites()
    PathInjector.annotation_init(config['paths'])
    return config


def test_director(config, pickle_location):
    """
    Unpickles tuple of tests and suites chosen by the user to be executed.
    Based on the selected tests, it creates configuration for Constable.
    @param pickle_location: File name of the pickled test information
    """

    test_env_path = config['paths']['test_env']
    scripts_path = config['paths']['scripts']
    test_location = config['paths']['test_location']
    authserver_start_cmd = config['authserver']['start_cmd']

    pickle_tests_path = os.path.join(scripts_path, pickle_location)
    execution_category = unpickle_tests(pickle_tests_path)
    log_guest(f"Test category to be run is {execution_category}")

    suites_to_run = TestRegistrator.get_test_suites_for(execution_category)

    # The testing environment dir contains all the files that we need to
    # reference
    os.chdir(test_env_path)
    make_authserver_config(scripts_path, test_env_path, config['authserver'])

    results = {}
    test_category_setup(test_env_path)
    for test_category, test_suites in suites_to_run.items():
        make_final_config(test_category, test_suites, scripts_path,
                          test_env_path, config['authserver']
                          )

        test_location_path = f'{test_location}/{test_category}'
        os.mkdir(test_location_path)
        new_results = start_suite(test_suites, authserver_start_cmd,
                                  test_location_path, test_env_path)
        #test_category_cleanup(test_env_path)

        results.update(new_results)
    print_class_report(results)


def test_category_setup(target_path):
    os.mkdir(f'{target_path}/allowed')
    os.mkdir(f'{target_path}/restricted')


def test_category_cleanup(target_path):
    shell = LocalShell()
    shell.execute_cmd(f"rm -rf {target_path}/allowed")
    shell.execute_cmd(f"rm -rf {target_path}/restricted")


def start_suite(suites, authserver_start_cmd, test_location_path,
                target_location):
    """
    Main testing function, starts Constable and executes suites one after the
    other. When all testing is done, results are sent to the validator module
    to be validated.
    @param suites: (list) test suites to be executed
    @param authserver_start_cmd: (str) authserver start command
    @returns (dict) of results from testing in {'test_name': is_passed_boolean}
    key-value pairs
    """

    def setup_environment(test_suite):
        log_guest(f'Setup of environment for {test_suite.__class__.__name__}')
        tests = test_suite.tests
        for test in tests:
            test_name = test[0]
            random_target_dir = uuid.uuid4().hex
            test_location = f'{test_location_path}/{test_name}'
            os.mkdir(test_location)
            os.chdir(test_location)
            test_suite._test_setup(target_location, random_target_dir)

    def execute_suites(suites):
        os.chdir(target_location)
        log_guest('Starting Constable')
        constable = Reader(authserver_start_cmd)

        time.sleep(1)
        log_guest('Starting test batch')
        results = execute_tests(suites, test_location_path)

        log_guest('Terminating Constable')
        constable.terminate()
        return results

    #def cleanup_environment(suite_cleanups):
    #    log_guest('Cleanup of environment after testing')
    #    for suite_cleanup in suite_cleanups:
    #        suite_cleanup()

    #(suite_setups, suite_cleanups) = get_setup_and_cleanup_routines(suites)

    for suite in suites:
        setup_environment(suite)
    results = execute_suites(suites)

    return results


def make_authserver_config(scripts_path, test_env_path, authserver_config):
    """
    Creates config for chosen authorization server
    @param scripts_path: path to the MITS scripts on guest machine
    @param test_env_path: path to testing environment on guest machine
    @param authserver_config: (dict) configuration settings for authorization
    server
    """
    authserver_name = authserver_config['name']
    config_extension = authserver_config['config_extension']

    log_guest(f'Creating configuration for authserver {authserver_name}')
    old_config_path = f'{scripts_path}/{authserver_name}.{config_extension}'
    new_config_path = f'{test_env_path}/{authserver_name}.{config_extension}'
    with open(new_config_path, 'w') as config_out:
        with open(old_config_path, "r") as config_file:
            config_content = config_file.read()
            config_content = PathInjector.inject_paths(config_content)
            config_out.write(config_content)


def make_final_config(test_category, test_suites, scripts_path, test_env_path,
                      authserver_config):
    config_extension = authserver_config['config_extension']
    """
    Creates configuration file based on chosen testing suites.
    @param test_category: test category of executed test suites. Test category
    is important for correct choice of base config
    @param test_suites: (list) of test suites to be executed
    @param scripts_path: (str) path to MITS scripts on guest machine
    @param test_env_path: (str) path to testing environment on guest machine
    @param authserver_config: configuration settings for authorization server
    """
    def get_required_configs():
        """
        Get config filenames for @test_suites
        @returns list of config filenames
        """
        base_config = f'{scripts_path}/{test_category}.{config_extension}'
        config_filenames = [base_config]
        log_guest(config_filenames)
        for test_suite in test_suites:
            filename = test_suite.__class__.__name__.lower()
            suite_config_file = f'{scripts_path}/{filename}.{config_extension}'
            config_filenames.append(suite_config_file)
            log_guest(f"Config {filename} appended to list")
        return config_filenames

    log_guest(f'Creating configuration /medusa.conf for {test_category}')
    config_filenames = get_required_configs()
    with open(f'{test_env_path}/medusa.conf', 'w') as config_out:
        for config_filename in config_filenames:
            with open(config_filename, "r") as config_file:
                config_content = config_file.read()
                config_content = PathInjector.inject_paths(config_content)
                config_out.write(config_content)


def execute_tests(test_suites, test_location):
    """
    Routine for execution of tests from provided test_suites
    @param test_suites: list of test suites, from which tests are being
    executed
    @returns (dict) of results from testing in {'test_name': is_passed_boolean}
    key-value pairs
    """
    results = {}
    for test_suite in test_suites:
        tests = test_suite.tests
        for test_name, test_case in tests:
            log_guest(f'Executing test {test_name}: {test_case}')
            os.chdir(f'{test_location}/{test_name}')
            results[test_name] = str(test_case())
    return results


def print_class_report(results):
    """
    Temporary routine for reporting results to host machine
    @param results: (dict) of results from testing in
    {'test_name': is_passed_boolean} key-value pairs
    """
    headers = ['Test name', 'Is passed']
    rows = [(name, result) for name, result in results.items()]
    print(tabulate.tabulate(rows, headers=headers))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    config = init()
    test_director(config, sys.argv[1])
