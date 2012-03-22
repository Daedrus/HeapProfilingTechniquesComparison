CC = g++
CFLAGS = -Wall
LDFLAGS = -lrt

MAX_DEPTH = 8
NR_ITERATIONS = 1
START_SIZE = pgsz
END_SIZE = 100*pgsz
STEP_SIZE = pgsz

allocate: allocate.c allocate.h
	$(CC) -o $@ $< $(CFLAGS) $(LDFLAGS)

allocate.h:
	python allocgen.py $(MAX_DEPTH) $(NR_ITERATIONS) $(START_SIZE) $(END_SIZE) $(STEP_SIZE) > allocate.h

run:
	./allocate

.PHONY: clean
clean:
	\rm allocate.h allocate
