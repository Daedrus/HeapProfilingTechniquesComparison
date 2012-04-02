#!/usr/src/python

import argparse

import matplotlib.pyplot as plt

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import os

class Scenario:
	def __init__(self, name, path):
		self.name = name
		self.path = path
		self.results = []

	def __str__(self):
		return self.name + ", " + self.path

basic_scenario = Scenario("0.basic", "./basic")
allocation_size_scenarios = sorted([Scenario(x, os.path.join("./allocationsize/", x)) for x in os.listdir("./allocationsize")], key=lambda scenario: scenario.name)
allocation_point_scenarios = sorted([Scenario(x, os.path.join("./allocationpoint/", x)) for x in os.listdir("./allocationpoint")], key=lambda scenario: scenario.name)

# From http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks
def flatten(x):
	result = []
	for el in x:
		#if isinstance(el, (list, tuple)):
		if hasattr(el, "__iter__") and not isinstance(el, basestring):
			result.extend(flatten(el))
		else:
			result.append(el)
	return result

def setup(defines):
	print "Building basic scenario ..."
	call(flatten(["make", defines, "-C", basic_scenario.path]))

	print "Building allocation size scenarios ..."
	for scenario in allocation_size_scenarios:
		call(flatten(["make", defines, "-C", scenario.path]))

	print "Building allocation point scenarios ..."
	for scenario in allocation_point_scenarios:
		call(flatten(["make", defines, "-C", scenario.path]))

def run_scenario(scenario, times):
	for i in range(0, times):
		process=Popen(["make", "run", "-C", scenario.path], stdout=PIPE)
		process.wait()
		scenario.results.append(long(process.communicate()[0].split('\n')[2]))

def run(times):
	print "Running basic scenario", times, "times ..."
	run_scenario(basic_scenario, times)

	print "Running allocation size scenarios", times, "times ..."
	for scenario in allocation_size_scenarios:
		run_scenario(scenario, times)

	print "Running allocation point scenarios", times, "times ..."
	for scenario in allocation_point_scenarios:
		run_scenario(scenario, times)

def clean():
	print "Cleaning basic scenario ..."
	call(["make", "clean", "-C", basic_scenario.path])

	print "Cleaning allocation size scenarios ..."
	for scenario in allocation_size_scenarios:
		call(["make", "clean", "-C", scenario.path])

	print "Cleaning allocation point scenarios ..."
	for scenario in allocation_point_scenarios:
		call(["make", "clean", "-C", scenario.path])

def run_test(max_depth, nr_iterations, start_size, end_size, step_size):
	defines = []
	defines.append('MAX_DEPTH=' + str(max_depth) + ' ')
	defines.append('NR_ITERATIONS=' + str(nr_iterations) + ' ')
	defines.append('START_SIZE=' + str(start_size) + ' ')
	defines.append('END_SIZE=' + str(end_size) + ' ')
	defines.append('STEP_SIZE=' + str(step_size) + ' ')

	setup(defines)
	run(20)
	clean()

	process_results(nr_iterations)

def process_results(nr_iterations):
	allocation_size_results = []
	allocation_size_results.append(basic_scenario.results)
	for scenario in allocation_size_scenarios:
		allocation_size_results.append(scenario.results)

	allocation_point_results = []
	allocation_point_results.append(basic_scenario.results)
	for scenario in allocation_point_scenarios:
		allocation_point_results.append(scenario.results)

	allocation_size_averages = [sum(x[1:])/(len(x)-1) for x in allocation_size_results]
	allocation_point_averages = [sum(x[1:])/(len(x)-1) for x in allocation_point_results]

	allocation_size_differences = [x - allocation_size_averages[0] for x in allocation_size_averages]
	allocation_point_differences = [x - allocation_point_averages[0] for x in allocation_point_averages]

	plt.subplot(211)
	plt.plot(allocation_size_differences, marker='o', linestyle=':', color=[0.2 + nr_iterations/float(1000000), 0, 0], label=str(nr_iterations))
	plt.subplot(212)
	plt.plot(allocation_point_differences, marker='o', linestyle=':', color=[0.2 + nr_iterations/float(1000000), 0, 0], label=str(nr_iterations))

plt.figure(1)
plot1 = plt.subplot(211)
plt.ylabel('microseconds')
plt.xticks(range(len(allocation_size_scenarios)+1), [basic_scenario.name]+[scenario.name for scenario in allocation_size_scenarios], size='large')
plot2 = plt.subplot(212)
plt.xlabel('test name')
plt.ylabel('microseconds')
plt.xticks(range(len(allocation_point_scenarios)+1), [basic_scenario.name]+[scenario.name for scenario in allocation_point_scenarios], size='large')

run_test(1, 50000, 128, 128, 128)
run_test(1, 100000, 128, 128, 128)
run_test(1, 150000, 128, 128, 128)
run_test(1, 200000, 128, 128, 128)
run_test(1, 250000, 128, 128, 128)

plt.legend(loc='upper center', fancybox=True, shadow=True, title='allocations')
plt.show()

