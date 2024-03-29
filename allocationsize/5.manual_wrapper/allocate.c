#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sched.h>

#include <malloc.h>

#include "allocate.h"

#define LOG_ALLOCATION_POINT

#ifdef LOG_ALLOCATION_POINT

#define BUFFER_SIZE 100
#define BUFFER_DEPTH 10

struct frame {
	struct frame* fr_savfp;
	long fr_savpc;
};

long allocation_points[BUFFER_SIZE][BUFFER_DEPTH];
unsigned int allocation_index = 0;

#endif 

unsigned long long allocatedsize;
unsigned long long counter;

void *mymalloc(size_t size)
{
#ifdef LOG_ALLOCATION_POINT
	struct frame *frame = (struct frame *)__builtin_frame_address(0);
	unsigned int depth_index = 0;

	for (struct frame *fp = frame; (!(fp < frame)) && depth_index < BUFFER_DEPTH;
		fp = (struct frame *)((long) fp->fr_savfp)) {
		allocation_points[allocation_index][depth_index] = fp->fr_savpc;
		allocation_index = (allocation_index % (BUFFER_SIZE - 1)) + 1;
	}
#endif

	void *ptr = malloc(size);

	allocatedsize += size;

	return ptr;
}

void myfree(void *ptr)
{
    free(ptr);
}

struct node *list;

unsigned long long pgsz;

struct node {
	char *data;
	unsigned long long size;
	struct node *next;
};

void add_node(unsigned long long size)
{
	struct node *new_node = (struct node*)mymalloc(sizeof(struct node));
	new_node->data = (char*)mymalloc(size);
	new_node->size = size;
	new_node->next = list;

#ifdef DIRTY_ENABLED
	for (unsigned long long i = 0; i < size; i += pgsz) {
		new_node->data[i] = 42;
	}
#endif

	if ((counter++) % 2) {
		free(new_node->data);
		new_node->data = NULL;
	}

	list = new_node;
}

void allocate()
{
	for (int j = 0; j < NR_ITERATIONS; j++) {
		for (unsigned long long size = START_SIZE; size <= END_SIZE; size+=STEP_SIZE) {
			funcs[MAX_DEPTH-1](size);
		}
	}
}

void print_list()
{
	struct node *it = list;

	while(it != NULL) {
		printf("%llu\n", it->size);
		it = it->next;
	}
}

// Proper time diffing from http://www.guyrutenberg.com/2007/09/22/profiling-code-using-clock_gettime/
void print_time_diff(timespec start, timespec end)
{
	timespec diff;

	if ((end.tv_nsec-start.tv_nsec) < 0) {
		diff.tv_sec = end.tv_sec - start.tv_sec - 1;
		diff.tv_nsec = 1000000000 + end.tv_nsec - start.tv_nsec;
	} else {
		diff.tv_sec = end.tv_sec - start.tv_sec;
		diff.tv_nsec = end.tv_nsec - start.tv_nsec;
	}

	printf("%lu\n", (diff.tv_sec * 1000000000) + diff.tv_nsec);
}

int main(int argc, char **argv)
{
	cpu_set_t mask;
	timespec start, end;
	list = NULL;

	CPU_ZERO(&mask);
	CPU_SET(0, &mask);
	sched_setaffinity(0, sizeof(mask), &mask);

	pgsz = sysconf(_SC_PAGESIZE);

	allocatedsize = 0;

	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
	allocate();
	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);

	print_time_diff(start, end);

	return 0;
}
