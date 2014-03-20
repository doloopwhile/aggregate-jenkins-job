#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen
import urllib.request

from operator import itemgetter

import pyjq as jq
import math

import webbrowser

def main():
    parser = ArgumentParser()
    parser.add_argument('host', action='store')
    parser.add_argument('job', action='store')
    parser.add_argument('--port', action='store', default=80)

    args = parser.parse_args()

    def api_url(url):
        return urljoin(url, 'api/json')

    job_api_url = api_url('http://{0.host}:{0.port}/job/{0.job}/'.format(args))

    # builds = []
    # for build_url in jq.all('.builds[].url', url=job_api_url):
    #     build = jq.one('{duration: .duration, number: .number, result: .result}', url=api_url(build_url))
    #     builds.append(build)

    builds = [{'number': 415, 'duration': 1817465, 'result': 'SUCCESS'}
    ,{'number': 416, 'duration': 1490033, 'result': 'SUCCESS'}
    ,{'number': 419, 'duration': 1803128, 'result': 'SUCCESS'}
    ,{'number': 421, 'duration': 1753199, 'result': 'SUCCESS'}
    ,{'number': 426, 'duration': 1686575, 'result': 'SUCCESS'}
    ,{'number': 427, 'duration': 2449128, 'result': 'SUCCESS'}
    ,{'number': 428, 'duration': 1752961, 'result': 'SUCCESS'}
    ,{'number': 429, 'duration': 1424184, 'result': 'SUCCESS'}
    ,{'number': 430, 'duration': 1540526, 'result': 'SUCCESS'}
    ,{'number': 431, 'duration': 1776849, 'result': 'SUCCESS'}
    ,{'number': 432, 'duration': 1380645, 'result': 'SUCCESS'}
    ,{'number': 433, 'duration': 2087693, 'result': 'SUCCESS'}
    ,{'number': 435, 'duration': 1629043, 'result': 'SUCCESS'}]
    builds = [build for build in builds if build['result'] == 'SUCCESS']
    builds.sort(key=itemgetter('number'))

    import string
    import json
    graph_data = [['build', 'duration']] + [[str(b['number']), (b['duration'] // 1000 / 60)] for b in builds]

    from pprint import pprint

    pprint(graph_data)

    pprint([
        ['x', 'Blanket 2'],
        ['A',    0.5],
        ['B',    1],
        ['C',    0.5],
        ['D',    1],
        ['E',    0.5],
        ['F',    1],
        ['G',    0.5],
        ['H',    1],
        ['I',    0.5],
        ['J',    1],
        ['K',    0.5],
        ['L',    1],
        ['M',    0.5],
        ['N',    1]
    ])
    html = string.Template('''\
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>
      Google Visualization API Sample
    </title>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {packages: ['corechart']});
    </script>
    <script type="text/javascript">
      function drawVisualization() {
        // Create and populate the data table.
        var data = google.visualization.arrayToDataTable($json_graph_data);
        // Create and draw the visualization.
        new google.visualization.LineChart(document.getElementById('visualization')).
            draw(data, {curveType: "none",
                        width: 800, height: 400,
                        vAxis: {maxValue: 10}}
                );
      }

      google.setOnLoadCallback(drawVisualization);
    </script>
  </head>
  <body style="font-family: Arial;border: 0 none;">
    <div id="visualization" style="width: 500px; height: 400px;"></div>
  </body>
</html>''').substitute(json_graph_data=json.dumps(graph_data))

    import tempfile

    t = tempfile.NamedTemporaryFile(delete=False)
    t.write(html.encode('ascii'))
    t.close()
    from pathlib import Path
    webbrowser.open(Path(t.name).as_uri())



if __name__ == '__main__':
    main()
