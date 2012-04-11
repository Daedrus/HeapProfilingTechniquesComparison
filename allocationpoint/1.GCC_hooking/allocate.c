#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include <malloc.h>

#include "allocate.h"

unsigned long long counter;

static void my_init_hook (void);
static void *my_malloc_hook (size_t, const void *);
static void my_free_hook (void*, const void *);

static void *(*old_malloc_hook) (size_t, const void *);
static void (*old_free_hook) (void*, const void *);

void (*__malloc_initialize_hook) (void) = my_init_hook;

static void my_init_hook (void)
{
	old_malloc_hook = __malloc_hook;
	old_free_hook = __free_hook;
	__malloc_hook = my_malloc_hook;
	__free_hook = my_free_hook;
}

static void * my_malloc_hook (size_t size, const void *caller)
{
	void *result;
	const void *tmp;

	__malloc_hook = old_malloc_hook;
	__free_hook = old_free_hook;

	result = malloc(size);

	old_malloc_hook = __malloc_hook;
	old_free_hook = __free_hook;

	tmp = caller;
	//printf("%p\n", caller);

	__malloc_hook = my_malloc_hook;
	__free_hook = my_free_hook;

	return result;
}

static void my_free_hook (void *ptr, const void *caller)
{
	__malloc_hook = old_malloc_hook;
	__free_hook = old_free_hook;

	free(ptr);

	old_malloc_hook = __malloc_hook;
	old_free_hook = __free_hook;

	__malloc_hook = my_malloc_hook;
	__free_hook = my_free_hook;
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

int main(int argc, char **argv)
{
	timespec start, end;
	list = NULL;

	pgsz = sysconf(_SC_PAGESIZE);

	counter = 0;

	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
	allocate();
	clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);

	print_time_diff(start, end);

	return 0;
}
