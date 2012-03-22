#!/usr/bin/python

import sys

print "#ifndef ALLOCATE_H"
print "#define ALLOCATE_H"
print "#include \"StackLogger.h\""

print "#define MAX_DEPTH " + sys.argv[1]
print "#define NR_ITERATIONS " + sys.argv[2]

print "#define START_SIZE " + sys.argv[3]
print "#define END_SIZE " + sys.argv[4]
print "#define STEP_SIZE " + sys.argv[5]

print "#define DIRTY_ENABLED"

print "extern StackLogger *logger;"
print "void add_node(unsigned long long size);"

print "void func0(unsigned long long size) {"
print "logger->enterFunction((const void*)&func0);"
print "add_node(size);"
print "logger->leaveFunction();"
print "}"

for i in range(1, int(sys.argv[1])):
	print "void func" + str(i) + "(unsigned long long size) {"
	print "logger->enterFunction((const void*)&func" + str(i) + ");"
	print "func" + str(i-1) + "(size);"
	print "logger->leaveFunction();"
	print "}"

print "void (*funcs[MAX_DEPTH]) (unsigned long long size) = {"
for i in range(0, int(sys.argv[1])):
	print "func" + str(i) + ","
print "};"

print "#endif"
