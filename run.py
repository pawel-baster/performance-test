#!/usr/bin/env python
'''
pawel at May 21, 2012
'''

# urls to test
urls = {
	'http://domain/index.php',
	'http://domain/newest.php',
}

resultsFile = 'results.pickle'
outputFile = 'performance.png'

# number of connections to average over
count = 100

import subprocess
import re
import os
import datetime
import pickle
import matplotlib as mpl
# required if no x-server is running
mpl.use('Agg')
import pylab
# requires python-matplotlib package
from matplotlib.patches import Polygon

class AbLoadTestRunner:

	def __init__(self, saver, view):
		self._saver = saver
		self._view = view

	def run(self, urls):
		print 'using ab to measure performance of given sites...'
		stats = self._saver.loadTestResults()
		for url in urls:
			print 'testing ' + url
			results = subprocess.check_output(['ab', '-n %d' % count, '-c 1', url], stderr=subprocess.STDOUT)
			if url not in stats['response']:
				stats['response'][url] = list()

			stats['response'][url].append(self._parseResult(results))
			
		self._saver.saveTestResults(stats)
		self._view.show(stats)

	def _parseResult(self, res):
		m = re.search('Total:\s+\d+\s+(\d+)\s+([\d.]+)\s+\d+\s+\d+', res)
		assert m is not None, 'Unexpected output %s' % res
		mean = int(m.group(1))
		sd = float(m.group(2))
		return (mean, sd)


class CsvSaver:

	def __init__(self, filename):
		self._filename = filename

	def loadTestResults(self):
		if os.path.exists(self._filename):
			with open(self._filename, 'r') as f:
		            return pickle.load(f)
		else:
			return {'response' : {}}

	def saveTestResults(self, results):
		sfile = open(self._filename, 'w')
        	pickle.dump(results, sfile)
        	sfile.close()

class PylabView:
	
	def __init__(self, outputFile):
		self._outputFile = outputFile

	def show(self, results):
		i = 1
		for url, case in results['response'].items():
			ax = pylab.subplot(2,2,i)
			x = range(len(case))

			mean = [z[0] for z in case]
			upper = [z[0] + 2*z[1] for z in case]
			lower = [z[0] - 2*z[1] for z in case]

			pylab.plot(x, mean, linewidth=1)
			pylab.ylim([0.9*min(lower), 1.1*max(upper)])
			pylab.title(url, fontsize=10)

			verts = zip(x, lower) + list(reversed(zip(x, upper)))
			poly = Polygon(verts, facecolor='0.8', edgecolor='0.8')
			ax.add_patch(poly)
			i = i + 1

		pylab.savefig(self._outputFile)		
			
saver = CsvSaver(resultsFile)
view = PylabView(outputFile)
runner = AbLoadTestRunner(saver, view)
runner.run(urls)	
