#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
import shutil
from urllib.parse import urljoin
from urllib.request import urlopen
import urllib.request
from zipfile import ZipFile
import io
from contextlib import ExitStack

import pyjq as jq

def create_empty_dir(dirpath):
    if not dirpath.is_dir():
        dirpath.mkdir(parents=True)
        return
    else:
        for entry in Path(dirpath).glob('*'):
            shutil.rmtree(str(entry))


def main():
    parser = ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port')
    parser.add_argument('job')
    parser.add_argument('build_number', nargs='?', default='lastSuccessfulBuild')
    parser.add_argument('-o', '--output-dir', action='store', dest='output_dir', default='artifacts')
    parser.add_argument('--console-text', '-c', action='store_true', dest='console_text')

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    create_empty_dir(output_dir)

    def api_url(url):
        return urljoin(url, 'api/json')

    build_api_url = api_url('http://{0.host}:{0.port}/job/{0.job}/{0.build_number}/'.format(args))
    for run_url in jq.all('.runs[].url', url=build_api_url):
        subjob_url = urljoin(run_url, '../')
        subjob_name = jq.one('.displayName', url=api_url(subjob_url))
        subjob_dir = output_dir / urllib.request.quote(subjob_name, '')

        if not subjob_dir.is_dir():
            subjob_dir.mkdir(parents=True)

        with (subjob_dir / 'consoleText').open('wb') as local_fp, \
             urlopen(urljoin(run_url, 'consoleText')) as http_fp:
            shutil.copyfileobj(http_fp, local_fp)

        zip_fp = io.BytesIO(urlopen(urljoin(run_url, 'artifact/*zip*/archive.zip')).read())
        with ZipFile(zip_fp) as z:
            for name in z.namelist():
                prefix = 'archive/'
                if not name.startswith(prefix): continue

                path = subjob_dir / name[len(prefix):]
                if not path.parent.is_dir():
                    path.parent.mkdir(parents=True)
                with path.open('wb') as fp:
                    fp.write(z.read(name))


if __name__ == '__main__':
    main()
