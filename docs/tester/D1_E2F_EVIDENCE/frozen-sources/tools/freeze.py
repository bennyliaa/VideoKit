import argparse
import sys
sys.dont_write_bytecode = True
from package_support import seal_package
if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:seal_package()
    else:print('INSPECT_ONLY: --freeze seals offline files, never reserves or runs a batch')
