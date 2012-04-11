#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include <malloc.h>

#include "allocate.h"

unsigned long long allocatedsize;
unsigned long long counter;

struct node *list;

unsigned long long pgsz;

struct node {
	char *data;
	unsigned long long size;
	struct node *next;
};

void add_node(unsigned long long size)
{
	struct node *new_node = (struct node*)malloc(sizeof(struct node));
	new_node->data = (char*)malloc(size);
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

void get_list_size()
{
	struct node *it = list;

	while(it != NULL) {
		allocatedsize += malloc_usable_size(it->data);
		allocatedsize += malloc_usable_size(it);
		it = it->next;
	}
}

int main(int argc, char **argv)
{
	timespec start, end;
	list = NULL;

	pgsz = sysconf(_SC_PAGESIZE);

	allocatedsize = 0;
	counter = 0;

	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
	allocate();
	get_list_size();
	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);

	print_time_diff(start, end);

	return 0;
}
