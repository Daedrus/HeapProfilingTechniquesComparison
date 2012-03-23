#!/usr/src/python

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import os

BASIC_SCENARIO = "./basic"
ALLOCATION_SIZE_SCENARIOS = [os.path.join("./allocationsize/", x) for x in os.listdir("./allocationsize")]
ALLOCATION_POINT_SCENARIOS = [os.path.join("./allocationpoint/", x) for x in os.listdir("./allocationpoint")]

results=[]

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
		results[-1].append(process.communicate()[0].split('\n')[2])


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

setup()
run(10)
clean()

print results
