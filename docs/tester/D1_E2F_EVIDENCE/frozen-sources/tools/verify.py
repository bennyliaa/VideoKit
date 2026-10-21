import argparse
import sys
sys.dont_write_bytecode = True
from package_support import verify_package
if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--expected-freeze');args=parser.parse_args()
    verify_package(args.expected_freeze)
