"""@package mte.validator
Validates outputs of executed test suites.
"""
import config


class Validator:
    """
    This class validates test results and prepares data for the report module. It uses output_expect and dmesg_expect
    properties of tests.
    """
    @classmethod
    def validate(cls, results, outputs):
        """ Decides which validation strategy to choose based on the used suite.
        @param results: List of outputs. Its keys may vary based on the used suite, but it should contain at least
        system_log and constable keys.
        @param outputs: If using serial suite, than it's None. Else, it is a list of dictionaries containg two keys:
        test (name of the test) and output (output of the system call).
        @return: Tuple of results and outputs.
        """
        if outputs is None:
            results = cls.__validate_results(results)
        else:
            outputs = cls.__validate_concurrent_results(results, outputs)
        return results, outputs

    @staticmethod
    def __validate_results(results):
        """
        Validates results from serial test suite. It uses just results list.
        @param results: List of dictionaries containing test, output, system_log and constable information.
        @return: Validated results. Adds new fields to dictionaries: output_valid, dmesg_valid and constable_valid.
        These can be True or False.
        """
        # We are checking output for nothing except the fork
        # Dmesg for name of the test, or maybe an expectation words
        # Constable for runtime errors
        for test in results:
            # Checking the output of commands
            if config.tests[test['test']]['output_expect'] is None:
                if test['output'] == '':
                    test['output_valid'] = True
                else:
                    test['output_valid'] = False
            elif type(config.tests[test['test']]['output_expect']) is str:
                if test['output'].find(config.tests[test]['test']) != -1:
                    test['output_valid'] = True
                else:
                    test['output_valid'] = False
            elif type(config.tests[test['test']]['output_expect']) is list:
                for s in config.tests[test['test']]['output_expect']:
                    if s not in test['output']:
                        test['output_valid'] = False
                        break
                else:
                    test['output_valid'] = True
            # Checking the dmesg
            if config.tests[test['test']]['dmesg_expect'] in test['system_log']:
                test['dmesg_valid'] = True
            else:
                test['dmesg_valid'] = False
            # Checking constable
            # TODO case insensitive
            if 'error' in test['constable']:
                test['constable_valid'] = False
            else:
                test['constable_valid'] = True
        return results

    @staticmethod
    def __validate_concurrent_results(results, outputs):
        """ Used when validating concurrent results. Searches for system call names in dmesg and errors in constable.
        @param results: Dictionary containing dmesg and constable outputs.
        @param outputs: List of dictionaries containing outputs of executed system calls.
        @return: List of dictionaries, that contain boolean keys: output_valid, dmesg_valid and constable_valid.
        """
        # Check outputs similarly to serial tests
        # Check full dmesg for name of the tests
        # Full Constable for errors, but won't be able to locate exact cause of the error
        for out in outputs:
            # Checking the output of commands
            if config.tests[out['test']]['output_expect'] is None:
                if out['output'] == '':
                    out['output_valid'] = True
                else:
                    out['output_valid'] = False
            elif type(config.tests[out['test']]['output_expect']) is str:
                if out['output'].find(config.tests[out]['test']) != -1:
                    out['output_valid'] = True
                else:
                    out['output_valid'] = False
            elif type(config.tests[out['test']]['output_expect']) is list:
                for s in config.tests[out['test']]['output_expect']:
                    if s not in out['output']:
                        out['output_valid'] = False
                        break
                else:
                    out['output_valid'] = True
            # Checking the dmesg
            if config.tests[out['test']]['dmesg_expect'] in results['system_log']:
                out['dmesg_valid'] = True
            else:
                out['dmesg_valid'] = False
            # Checking constable
            # TODO case insensitive
            if 'error' in results['constable']:
                out['constable_valid'] = False
            else:
                out['constable_valid'] = True
        return outputs
