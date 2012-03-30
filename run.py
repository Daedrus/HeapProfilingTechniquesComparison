#!/usr/src/python

import argparse

import matplotlib.pyplot as plt

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import os

BASIC_SCENARIO = "./basic"
ALLOCATION_SIZE_SCENARIOS = [os.path.join("./allocationsize/", x) for x in os.listdir("./allocationsize")]
ALLOCATION_POINT_SCENARIOS = [os.path.join("./allocationpoint/", x) for x in os.listdir("./allocationpoint")]

allocation_size_scenarios = [BASIC_SCENARIO] + ALLOCATION_SIZE_SCENARIOS
allocation_point_scenarios = [BASIC_SCENARIO] + ALLOCATION_POINT_SCENARIOS
results=[]

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
	call(flatten(["make", defines, "-C", BASIC_SCENARIO]))

	print "Building allocation size scenarios ..."
	for scenario in ALLOCATION_SIZE_SCENARIOS:
		call(flatten(["make", defines, "-C", scenario]))

	print "Building allocation point scenarios ..."
	for scenario in ALLOCATION_POINT_SCENARIOS:
		call(flatten(["make", defines, "-C", scenario]))

def run_scenario(scenario, times):
	for i in range(0, times):
		process=Popen(["make", "run", "-C", scenario], stdout=PIPE)
		process.wait()
		results[-1].append(long(process.communicate()[0].split('\n')[2]))


def run(times):
	del results[:]

	print "Running basic scenario", times, "times ..."
	results.append([BASIC_SCENARIO])
	run_scenario(BASIC_SCENARIO, times)

	print "Running allocation size scenarios", times, "times ..."
	for scenario in ALLOCATION_SIZE_SCENARIOS:
		results.append([scenario])
		run_scenario(scenario, times)

	print "Running allocation point scenarios", times, "times ..."
	for scenario in ALLOCATION_POINT_SCENARIOS:
		results.append([scenario])
		run_scenario(scenario, times)

def clean():
	print "Cleaning basic scenario ..."
	call(["make", "clean", "-C", BASIC_SCENARIO])

	print "Cleaning allocation size scenarios ..."
	for scenario in ALLOCATION_SIZE_SCENARIOS:
		call(["make", "clean", "-C", scenario])

	print "Cleaning allocation point scenarios ..."
	for scenario in ALLOCATION_POINT_SCENARIOS:
		call(["make", "clean", "-C", scenario])

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
	averages = [sum(x[1:])/(len(x)-1) for x in results]
	differences = [x - averages[0] for x in averages]

	print differences

	plt.subplot(211)
	plt.plot(differences[:len(allocation_size_scenarios)], marker='o', linestyle=':', color=[0.2 + nr_iterations/float(1000000), 0, 0], label=str(nr_iterations))
	plt.subplot(212)
	plt.plot(differences[-len(allocation_point_scenarios):], marker='o', linestyle=':', color=[0.2 + nr_iterations/float(1000000), 0, 0], label=str(nr_iterations))


plt.figure(1)
plt.subplot(211)
plt.xlabel('test name')
plt.ylabel('microseconds')
plt.xticks(range(len(allocation_size_scenarios)), allocation_size_scenarios, size='small', rotation=80)
plt.subplot(212)
plt.xlabel('test name')
plt.ylabel('microseconds')
plt.xticks(range(len(allocation_point_scenarios)), allocation_point_scenarios, size='small', rotation=80)

run_test(1, 50000, 128, 128, 128)
run_test(1, 100000, 128, 128, 128)
run_test(1, 150000, 128, 128, 128)
run_test(1, 200000, 128, 128, 128)
run_test(1, 250000, 128, 128, 128)

plt.legend(title='allocations')
plt.show()

