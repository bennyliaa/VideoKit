"""Finite future validation child. Inert until separately authorized execution."""
import sys
def main():
    if sys.argv[1:] not in (['ok'],['fail']):raise ValueError('FIXED_CHILD_MODE')
    print('OWNED_DRIVER_CHILD_ONLY',flush=True)
    return 0 if sys.argv[1]=='ok' else 7
if __name__=='__main__':raise SystemExit(main())
