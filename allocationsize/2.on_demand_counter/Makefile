CC = g++
CFLAGS = -Wall -O0
LDFLAGS = -lrt

MAX_DEPTH = 1
NR_ITERATIONS = 120000
START_SIZE = 128
END_SIZE = 128
STEP_SIZE = 128

allocate: allocate.c allocate.h
	$(CC) -o $@ $< $(CFLAGS) $(LDFLAGS)

allocate.h:
	python allocgen.py $(MAX_DEPTH) $(NR_ITERATIONS) $(START_SIZE) $(END_SIZE) $(STEP_SIZE) > allocate.h

run:
	./allocate

.PHONY: clean
clean:
	\rm allocate.h allocate
