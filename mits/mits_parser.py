import argparse
import tpm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_suites", help='the test suites to be run',
                        nargs="+")
    parser.add_argument("--run_sequentially",
                        help='run tests sequentially',
                        action='store_true')
    parser.add_argument("--run_concurrently",
                        help='run tests concurrently',
                        action='store_true')
    parser.add_argument("--run_class_tests",
                        help='run class tests',
                        action='store_true')
    args = parser.parse_args()

    to_run = None
    if(args.run_sequentially):
        to_run = ['do_tests']
    elif(args.run_concurrently):
        to_run = ['do_concurrent_tests']
    else:
        to_run = ['class_tests']

    if(args.test_suites):
        tpm.main(args.test_suites, to_run)
