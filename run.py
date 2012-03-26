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

results=[]

# From http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks
def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

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
		results[-1].append(int(process.communicate()[0].split('\n')[2]))


def run(times):
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

	#print defines.join()

	setup(defines)
	run(20)
	clean()

def process_results():
	scenarios = [x[0] for x in results]

	#print scenarios
	print [sum(x[1:])/(len(x)-1) for x in results]

	plt.plot([sum(x[1:])/(len(x)-1) for x in results], marker='o', linestyle='--', color='r')
	plt.xticks(range(len(scenarios)), scenarios, size='small', rotation=60)


# TEST CASE 1
run_test(8, 1, 'pgsz', '100*pgsz', 'pgsz')
process_results()

# TEST CASE 2
#run_test(8, 10000, 'pgsz', 'pgsz', 'pgsz')
#process_results()

plt.show()

