#!/usr/bin/env python3

import argparse
import re
import sys
from itertools import groupby


def noop(*_args, **_kwargs): pass


RE_SHARP = re.compile(r'^(?P<mark>#+)(?P<title>.*)$')
flag_show_position = False
verbose = noop


def fix_title(line):
    m = RE_SHARP.match(line)
    if m:
        mark = m.group('mark')
        title = m.group('title')
        if title[0] != ' ':
            line = mark + ' ' + title + '\n'
    return line


def fix_strong(line):
    pos = []
    idx = -2
    while True:
        idx = line.find('**', idx + 2)
        if idx < 0:
            break
        pos.append(idx)
    if not pos:
        return line

    ent = False
    space = []
    for idx in pos:
        pc = line[max(0, idx - 1):idx]
        nc = line[idx+2:idx+3]

        if ent:
            ent = not ent
            if nc and not nc.isspace():
                space.append(idx + 2)
            continue
        if not nc or nc == '\n':
            continue
        ent = not ent
        if pc and not pc.isspace():
            space.append(idx)

    pline = line
    for idx in reversed(space):
        line = line[:idx] + ' ' + line[idx:]
    return line


def qcfilter(file):
    with open(file) as fp:
        lines = fp.readlines()

    update = False
    markdown = True
    text = []
    for lno, line in enumerate(lines):
        if line[:3] == '```':
            markdown = not markdown
        if not markdown:
            text.append(line)
            continue

        prev = line
        line = fix_title(line)
        line = fix_strong(line)
        if prev != line:
            print(f'{file}:{lno+1}: {line.rstrip()}')
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
