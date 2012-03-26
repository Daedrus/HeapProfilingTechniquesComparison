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

defines=''

def setup():
	print "Building basic scenario ..."
	call(["make", "-C", BASIC_SCENARIO])

	print "Building allocation size scenarios ..."
	for scenario in ALLOCATION_SIZE_SCENARIOS:
		call(["make", "-C", scenario])

	print "Building allocation point scenarios ..."
	for scenario in ALLOCATION_POINT_SCENARIOS:
		call(["make", "-C", scenario])

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

#parser = argparse.ArgumentParser()
#parser.add_argument('--MAX_DEPTH', default=8)
#parser.add_argument('--NR_ITERATIONS', default=1)
#parser.add_argument('--START_SIZE', default='pgsz')
#parser.add_argument('--END_SIZE', default='100*pgsz')
#parser.add_argument('--STEP_SIZE', default='pgsz')

#args=parser.parse_args()

setup()
run(20)
clean()

scenarios = [x[0] for x in results]

print scenarios
print [sum(x[1:])/(len(x)-1) for x in results]

plt.plot([sum(x[1:])/(len(x)-1) for x in results], marker='o', linestyle='--', color='r')
plt.xticks(range(len(scenarios)), scenarios, size='small', rotation=60)
plt.show()

