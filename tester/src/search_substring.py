import argparse
import string
import random


def _parse_args():
    parser = argparse.ArgumentParser(description='Create random files with defined properties.')
    parser.add_argument('-S', '--size', 
        help='Specified file size, you can use, for example 7B, 52kB, 1MB, 4GB.', required=True)
    parser.add_argument('--output', help='path to otput file', default='.\\output.txt')
    parser.add_argument('--characters', default=2, type=int, choices=range(1, 27))
    parser.add_argument('--add-white-space', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    with open(args.output, 'w') as f:
        letters = string.ascii_lowercase[0:args.characters]
        if args.add_white_space:
            letters += ' \t\n'

        unit = args.size.lstrip('0123456789')
        size = int(args.size[:-len(unit)])

        if unit == 'kB':
            size *= 1024
        elif unit == 'MB':
            size *= 1024 * 1024
        elif unit == 'GB':
            size *= 1024 * 1024 * 1024
        elif unit != 'B':
            raise ValueError('Unsupported unit option ' + unit + '!')

        buf = ''
        for i in range(size):
            if i % 65536 == 0:
                f.write(buf)
                buf = ''

            buf += random.choice(letters)

        f.write(buf)
