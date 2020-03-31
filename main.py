import argparse

import adm0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Run without querying API')
    args = parser.parse_args()
    return args


def main(debug=False):
    adm0.main(debug=debug)


if __name__ == '__main__':
    args = parse_args()
    main(debug=args.debug)
