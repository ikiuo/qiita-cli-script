#!/usr/bin/env python3

import argparse
import re
import sys


def noop(*_args, **_kwargs): pass


RE_SHARP = re.compile(r'^(?P<mark>#+)(?P<title>.*)$')
flag_show_position = False
verbose = noop


def qcfilter(file):
    with open(file) as fp:
        lines = fp.readlines()

    update = False
    markdown = True
    text = []
    for lno, line in enumerate(lines):
        if line[:3] == '```':
            markdown = not markdown
        m = RE_SHARP.match(line) if markdown else None
        if m:
            mark = m.group('mark')
            title = m.group('title')
            if title[0] != ' ':
                if flag_show_position:
                    print(f'{file}:{lno+1}: {line.rstrip()}')
                line = mark + ' ' + title + '\n'
                update = True
        text.append(line)
    return (update, ''.join(text))


def main():
    global flag_show_position
    global verbose

    parser = argparse.ArgumentParser()
    # parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-U', '--update', action='store_true')
    parser.add_argument('-s', '--show-position', action='store_true')
    parser.add_argument('files', metavar='FILE', nargs='+')

    args = parser.parse_args()

    flag_show_position = args.show_position
    if args.verbose:
        verbose = print
    for file in args.files:
        update, text = qcfilter(file)
        verbose(f'update : {file}' if update else f'skip   : {file}')
        if update and args.update:
            with open(file, 'w') as fp:
                fp.write(text)


if __name__ == '__main__':
    main()
