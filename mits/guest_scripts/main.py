"""
@package mits.testing
This module executes tests and testing suites
"""
from asynchronous_reader import Reader
from logger import log_guest
import path_injector as PathInjector
import test_categories
import test_registrator as TestRegistrator
import test_settings

import os
import pickle
import shutil
import sys
import tabulate
import time
import uuid
import yaml


def main(pickle_location):
    with open("subconfig.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.Loader)

    test_env_path = config['paths']['test_env']
    tests_path = config['paths']['tests']
    scripts_path = config['paths']['scripts']
    authserver_config = config['authserver']

    test_settings.init(config['settings'])
    TestRegistrator.register_suites()
    PathInjector.annotation_init(config['paths'])
    exec_category = get_exec_category(scripts_path, pickle_location)
    suites_to_run = get_test_suites(exec_category)

    cleanup_dirs(test_env_path, tests_path)
    create_dirs(test_env_path, tests_path)

    setup_test_categories_in_test_env(suites_to_run.keys(), test_env_path,
                                      test_categories.setup_routines
                                      )
    setup_test_suite_dirs_in_tests(tests_path, test_env_path,
                                   suites_to_run
                                   )

    setup_base_authserver_configs(scripts_path, tests_path,
                                  suites_to_run.keys(),
                                  authserver_config
                                  )
    setup_testing_configs(scripts_path, tests_path, authserver_config,
                          suites_to_run
                          )
    results = start_testing(suites_to_run, tests_path, test_env_path,
                            authserver_config['start_cmd'])
    print_test_report(results)


def get_exec_category(scripts_path, pickle_filename):
    """
    Get exec category which is stored inside pickle file
    @param scripts_path: path to MITS scripts directory
    @param pickle_filename: name of pickle file
    @returns extracted exec category from pickle file as string
    """
    pickle_tests_path = os.path.join(scripts_path, pickle_filename)
    exec_category = unpickle_tests(pickle_tests_path)
    log_guest(f"Test category to be run is {exec_category}")
    return exec_category


def unpickle_tests(tests_path):
    """
    Reads pickled tests from test_path, which were pickled by host system.
    @param tests_path: Full path to the pickled data file.
    @return: Pickled data. It should be tuple of lists containing names of
    the tests and suites, respectively.
    """
    with open(tests_path, 'rb') as f:
        return pickle.load(f, fix_imports=True)


def get_test_suites(exec_category):
    """
    Get test suites for execution based on exec category
    @param exec_category: exec category for which the test suites shoudl be
    retrieved
    @returns the dict where keys are the test categories and values are lists
    of corresponding test suites
    """
    return TestRegistrator.get_test_suites_for(exec_category)


def cleanup_dirs(*args):
    """
    Delete recursively all content in dirs specified in args
    @param *args: directories to be removed
    """
    for dir_path in args:
        log_guest(f"Cleanup of {dir_path}")
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)


def create_dirs(*args):
    """
    Create dirs from *args
    @param *args: tuple of paths to directories, which should be created if do
    not exist
    """
    for path in args:
        if not os.path.isdir(path):
            log_guest(f"Creating dir {path}")
            os.mkdir(path)


def setup_test_categories_in_test_env(test_categories, test_env_path,
                                      setup_routines):
    """
    Setup dirs for test categories in test environment dir
    @param test_categories: list of test_categories, for which dirs should be
    created
    @param test_env_path: path to test environment as str
    @param setup_routines: dict, where key is test category and value is
    callback for setup of that test category
    """
    for test_category in test_categories:
        test_category_path = f'{test_env_path}/{test_category}'
        setup = setup_routines[test_category]
        setup(test_category_path)
        log_guest(f"Set up test category {test_category}")


def setup_test_suite_dirs_in_tests(tests_path, test_env_path, suites_to_run):
    """
    Setup environment for test suites, which should be run in tests path
    @param tests_path: tests path, where environment for test suites is created
    @param test_env_path: path to test environment
    @param suites_to_run: dict, where key is test category and value is tuple
    of test suites
    """
    def generate_dummy_dir_name():
        """
        Generate random name for dir
        """
        return uuid.uuid4().hex

    if not os.path.exists(tests_path):
        raise Exception("Tests dir not found")

    for test_category, test_suites in suites_to_run.items():
        tests_category_path = f'{tests_path}/{test_category}'
        for test_suite in test_suites:
            test_suite_name = test_suite.__class__.__name__
            test_suite_path = f'{tests_category_path}/{test_suite_name}'

            if not os.path.isdir(tests_category_path):
                os.mkdir(tests_category_path)

            os.mkdir(test_suite_path)
            tests = test_suite.tests
            for test_name, _ in tests:
                test_path = f'{test_suite_path}/{test_name}'
                os.mkdir(test_path)

                # the infrastructure is not very well designed, the test setup
                # is prepared from relative path, so we need to set current
                # test case as current dir
                os.chdir(test_path)

                dummy_dir = generate_dummy_dir_name()
                test_env_category_path = f'{test_env_path}/{test_category}'
                test_suite._test_setup(test_env_category_path, dummy_dir)

            log_guest(f"Set up dir for test suite {test_suite_name}")


def setup_base_authserver_configs(scripts_path, tests_path, test_categories,
                                  authserver_config):
    """
    Creates conf for chosen authorization server for each test category passed
    as argument
    @param scripts_path: path to the MITS scripts on guest machine
    @param tests_path: path to tests dir on guest machine
    @param test_categories: list of test categories (str)
    @param authserver_config: (dict) configuration settings for authorization
    server
    """
    authserver = authserver_config['name']
    conf_extension = authserver_config['config_extension']

    log_guest(f'Creating base config for {authserver}')
    for test_category in test_categories:
        test_category_path = f'{tests_path}/{test_category}'

        old_conf_path = f'{scripts_path}/{authserver}.{conf_extension}'
        new_conf_path = f'{test_category_path}/{authserver}.{conf_extension}'
        with open(new_conf_path, 'w') as conf_out:
            with open(old_conf_path, "r") as conf_file:
                conf_content = conf_file.read()
                conf_content = PathInjector.inject_paths(conf_content)
                conf_out.write(conf_content)


def setup_testing_configs(scripts_path, tests_path, authserver_config,
                          suites_to_run):
    config_extension = authserver_config['config_extension']
    """
    Creates configuration file based on chosen testing suites.
    @param scripts_path: (str) path to MITS scripts on guest machine
    @param tests_path: (str) path to tests dir
    @param authserver_config: configuration settings for authorization server
    @param suites_to_run: dict, where key is test category and value is tuple
    of test suites
    """
    def get_required_configs(scripts_path, test_category, test_suites):
        """
        Get config filenames for @test_suites
        @param scripts_path: (str) path to MITS scripts on guest machine
        @param test_category: test category for which the base config should
        be selected
        @param test_suites: suites for which we need to grab the configs
        @returns list of config filenames
        """
        base_config = f'{scripts_path}/{test_category}.{config_extension}'
        config_filenames = [base_config]
        for test_suite in test_suites:
            filename = test_suite.__class__.__name__.lower()
            suite_config_file = f'{scripts_path}/{filename}.{config_extension}'
            config_filenames.append(suite_config_file)
            log_guest(f"Config {filename} appended to list")
        return config_filenames

    for test_category, test_suites in suites_to_run.items():
        log_guest(f'Creating configuration /medusa.conf for {test_category}')
        conf_filenames = get_required_configs(scripts_path, test_category,
                                              test_suites)
        tests_category_path = f'{tests_path}/{test_category}'
        with open(f'{tests_category_path}/medusa.conf', 'w') as conf_out:
            for conf_filename in conf_filenames:
                with open(conf_filename, "r") as conf_file:
                    conf_content = conf_file.read()
                    conf_content = PathInjector.inject_paths(conf_content)
                    conf_out.write(conf_content)


def start_testing(suites_to_run, tests_path, test_env_path,
                  authserver_start_cmd):
    """
    Main testing function, starts Constable and executes suites one after the
    other. When all testing is done, results are sent to the validator module
    to be validated.
    @param suites_to_run: (dict), where key is test category and value is tuple
    of corresponding test suites
    @param tests_path: path to tests dir
    @param test_env_path: path to test environment dir
    @param authserver_start_cmd: (str) authserver start command
    @returns (dict) of results from testing in {'test_name': is_passed_boolean}
    key-value pairs
    """
    def copy_medusa_conf_to_test_env(src, dest):
        shutil.copyfile(f'{src}/medusa.conf', f'{dest}/medusa.conf')

    all_results = {}
    for test_category, test_suites in suites_to_run.items():
        test_category_path = f'{tests_path}/{test_category}'
        # it is required to copy medusa.conf file to test environment, because
        # this is where the authserver is going to search for the file
        copy_medusa_conf_to_test_env(test_category_path, test_env_path)

        # we need to change the dir to test_category_path because this is where
        # the authserver config is stored and being read
        os.chdir(test_category_path)

        log_guest('Starting authorization server')
        constable = Reader(authserver_start_cmd)

        time.sleep(1)
        log_guest('Starting test batch')
        results = execute_tests(test_suites, test_category_path)
        all_results[test_category] = results

        log_guest('Terminating authorization server')
        constable.terminate()

    return all_results


def execute_tests(test_suites, tests_category_path):
    """
    Routine for execution of tests from provided test_suites
    @param test_suites: list of test suites, from which tests are being
    executed
    @param test_category_path: path to test category being executed in tests
    dir
    @returns (dict) of results from testing in {'test_name': is_passed_boolean}
    key-value pairs
    """
    results = {}
    for test_suite in test_suites:
        tests = test_suite.tests
        suite_name = test_suite.__class__.__name__
        results[suite_name] = {}
        for test_name, test_case in tests:
            log_guest(f'Executing test {test_name}: {test_case}')
            os.chdir(f'{tests_category_path}/{suite_name}/{test_name}')
            results[suite_name][test_name] = str(test_case())
    return results


def print_test_report(results):
    """
    Temporary routine for reporting results to host machine
    @param results: (dict) of results from testing in
    {'test_name': is_passed_boolean} key-value pairs
    """
    headers = ['Test category', 'Test suite', 'Test name', 'Is passed']
    rows = []
    for test_category, test_suites in results.items():
        for test_suite_name, test_cases in test_suites.items():
            for test_name, test_result in test_cases.items():
                rows.append((test_category, test_suite_name,
                             test_name, test_result)
                            )
    print(tabulate.tabulate(rows, headers=headers))


if __name__ == "__main__":
    main(sys.argv[1])
