import argparse
import tpm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("category", help='the execution category to be run')
    args = parser.parse_args()

    tpm.main(args.category)
