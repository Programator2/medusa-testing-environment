# Introduction
The first version of MITS (previously called MTE - Medusa testing environment) was limited only to two scenarios per system call:
* deny
* allow

The development of MTE was resumed at 2020, where the project received new acronym MITS (Medusa Integration Testing System). The next release cycle should be completed around beginning of September of 2020.

# Features
- [x] Expanded possibilities of test execution to more scenarios
- [x] MITS runner via CLI
- [x] Configuration of test execution from host machine
- [x] Configurable choice of authorization server for testing execution
- [x] Configurable logger
- [x] Setup infrastructure for testing of offstream features
- [x] Implement grouping mechanism for tests (preparation for CI)
- [ ] Running each test in separate space (folder)
- [ ] Discovery of available partitions for mounting
- [ ] Cleanup of scripts folder on guest machine

## Expanded possibilities of test execution to more scenarios
Testing of system call should not be limited only to allow/deny path, but to anything which can be tested manually with shell in terminal.

## MITS runner via CLI
The MITS should not run tests from the GUI, but should use CLI instead.

## Configuration of test execution from host machine
In MTE, the config file consists from hard-coded tests that should be run. All configuration parameters for both host machine and guest machine should be easily configurable from Host machine.

## Configurable choice of authorization server for testing execution
The choice of authorization server should be easily configurable and should be matter of another switch in CLI or one-liner in configuration.

## Configurable logger
The logging messages have to be easily turned on or off based on CLI arguments or configuration.

## Setup infrastructure for testing of offstream features
The MITS framework should be able to support testing of features, which are not being part of Medusa upstream branch. Those offstream tests needs to form a separate group of tests and be executed only for branches with those offstream features.

## Implement grouping mechanism for tests (preparation for CI)
The tests should be divided into certain groups, which are then chosen by user with CLI. Only tests in that chosen group are being executed.

## Running each test in separate space (folder)
Each test needs to run in it’s separate instance, therefore each test should be separated in it’s own directory, which is later cleaned up.

## Discovery of available partitions for mounting
MITS has support for mount tests, but for now it would not run in all machines. In order to handle mount tests gracefully, we will need to provide some info to a user, whether there are any available partitions, which are then selected for test run and mounted.

## Cleanup of scripts folder on guest machine
Currently the scripts are short and there is a few of them. As the MITS project will grow, there can be possibility that the amount of transfered bytes will increase, therefore we need some mechanism which will speed up the process of transferring of files, while all required files are present there.
