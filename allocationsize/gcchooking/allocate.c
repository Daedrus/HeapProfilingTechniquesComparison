#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include <malloc.h>

#include "allocate.h"

unsigned long long allocatedsize;

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

	__malloc_hook = old_malloc_hook;
	__free_hook = old_free_hook;

	result = malloc(size);

	old_malloc_hook = __malloc_hook;
	old_free_hook = __free_hook;

	allocatedsize += size;
	//printf("%d %lld\n", size, allocatedsize);

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
	int *data;
	unsigned long long size;
	struct node *next;
};

void add_node(unsigned long long size)
{
	struct node *new_node = (struct node*)malloc(sizeof(struct node));
	new_node->data = (int*)malloc(size * sizeof(int));
	new_node->size = size;
	new_node->next = list;

#ifdef DIRTY_ENABLED
	for (unsigned long long i = 0; i < size; i += pgsz) {
		new_node->data[i] = 42;
	}
#endif

	list = new_node;
}

void allocate()
{
	for (int i = 0; i < MAX_DEPTH; i++) {
		for (int j = 0; j < NR_ITERATIONS; j++) {
			for (unsigned long long size = START_SIZE; size <= END_SIZE; size+=STEP_SIZE) {
				funcs[i](size);
			}
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
