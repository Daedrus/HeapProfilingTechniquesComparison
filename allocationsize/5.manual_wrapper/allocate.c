#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

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

int main(int argc, char **argv)
{
	timespec start, end, diff;
	unsigned long milis;
	list = NULL;

	pgsz = sysconf(_SC_PAGESIZE);

	allocatedsize = 0;

	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
	allocate();
	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);

	diff.tv_sec = end.tv_sec - start.tv_sec;
	diff.tv_nsec = end.tv_nsec - start.tv_nsec;

	milis = (diff.tv_sec * 1000000) + (diff.tv_nsec / 1000);

	printf("%lu\n", milis);
	//printf("%llu\n", allocatedsize);

	//print_list();

	//sleep(100);

	return 0;
}
