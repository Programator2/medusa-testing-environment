import argparse
import mits_init


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("category", help='the execution category to be run')
    parser.add_argument("--authserver",
                        help='the authserver to be used during testing')
    parser.add_argument("--verbose",
                        help='set verbosity for logging messages in GUEST',
                        action="store_true")
    args = parser.parse_args()

    mits_init.main(args.__dict__)
