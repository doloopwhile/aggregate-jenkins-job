#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
from operator import itemgetter
import argparse


class ItemTooLargeError(ValueError):
    pass


class FailedToPackError(ValueError):
    pass


# n個のグループに分ける。
# ただし、各グループのサイズはmax_group_volumeを超えないようにする
def pack_into_groups(n, max_group_volume, items, get_volume):
    items.sort(key=get_volume, reverse=True)

    for item in items:
        if get_volume(item) > max_group_volume:
            raise ItemTooLargeError(
                "{!r} is larger than max_group_volume {!r}".format(item, max_group_volume)
            )

    groups = [[[], 0] for _ in range(n)]

    for item in items:
        smallest_group = min(groups, key=itemgetter(1))

        smallest_group[0].append(item)
        smallest_group[1] += get_volume(item)

        if smallest_group[1] > max_group_volume:
            raise FailedToPackError('Failed to partition into {} groups'.format(n))
    return groups


# できるだけ少ないグループ数に収めようとする
def pack_into_groups_as_fewer(max_group_count, min_group_count, max_group_volume, items, get_volume):
    items = list(items)
    for n in range(1, max_group_count):
        try:
            return pack_into_groups(n, max_group_volume, items, get_volume)
        except ItemTooLargeError as e:
            raise e
        except ValueError as e:
            continue
    else:
        raise FailedToPackError('Failed to partition into {} groups'.format(
            max_group_count
        ))


def ascii_get_cell_width(text, irow, icol):
    return len(text)


def get_col_widths(rows, get_cell_width=ascii_get_cell_width):
    col_count = max(len(row) for row in rows)

    return [max(get_cell_width(row[icol]) for row in rows)
            for icol in range(col_count)]

def parse_tsv(fp):
    for row in csv.reader(fp, 'excel-tab'):
        try:
            yield dict(name=row[0], time=float(row[2]))
        except (IndexError, ValueError):
            pass


def write_script(groups, fp=sys.stdout):
    p = lambda *a, **kw: print(*a, file=fp, **kw)

    p("#!/bin/bash")
    p("rm -rf features.ci/feature/{1..99}")

    for features, _ in groups:
        for f in features:
            f['path'] = '../../../features/feature/' + f['name']

    path_width = max(len(f['path'])
        for features, _ in groups for f in features)


    for n, (features, total) in enumerate(groups, start=1):
        p("mkdir -p features.ci/feature/{}".format(n)
            + ' # {:02}:{:02}'.format(int(total // 60), int(total % 60)))

        for f in features:
           p("ln -s {} features.ci/feature/{} #{:02}:{:02}".format(
                f['path'].ljust(path_width),
                n,
                int(f['time'] // 60),
                int(f['time'] % 60)
            ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tsv_file', type=argparse.FileType())
    parser.add_argument('--max-duration', type=int, default=20)
    parser.add_argument('--min-group-count', type=int, default=9)
    parser.add_argument('--max-group-count', type=int, default=15)
    opts = parser.parse_args()

    groups = pack_into_groups_as_fewer(
        opts.max_group_count,
        opts.min_group_count,
        opts.max_duration * 60,
        parse_tsv(opts.tsv_file),
        itemgetter('time'),
    )

    write_script(groups)


if __name__ == '__main__':
    main()
