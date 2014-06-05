#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
import re
from operator import itemgetter
from itertools import groupby


def main():
    parser = ArgumentParser()
    parser.add_argument('artifact_dir', action='store')
    parser.add_argument('-s', '--sum', action='store_true', dest='sum')
    args = parser.parse_args()

    items = []
    for path in Path(args.artifact_dir).rglob('custom-junit/*.xml'):
        m = re.match(r'TEST-features\.ci-feature-(?P<group>(ie-)?.*?)-(?P<feature>.*).xml', path.name)

        group_number = m.group('group')
        feature_name = m.group('feature') + '.feature'
        with path.open() as fp:
            for line in fp:
                m = re.match(r'<testsuite .* time="(.*?)"', line)

                if not m:
                    continue
                items.append((feature_name, group_number, float(m.group(1))))
                break

    items.sort(key=itemgetter(1))

    if args.sum:
        for n, group in groupby(items, itemgetter(1)):
            s = sum(float(item[2]) for item in group) / 60
            s = str(round(s, 1))
            print('\t'.join([n, s]))
    else:
        for item in items:
            print('\t'.join(map(str, item)))



if __name__ == '__main__':
    main()
