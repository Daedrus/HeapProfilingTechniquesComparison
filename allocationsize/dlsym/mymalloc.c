#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>

unsigned long long allocatedsize = 0;

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

void* malloc(size_t size)
{
#ifdef LOG_ALLOCATION_POINT
	struct frame *frame;
	struct frame *fp;
	asm("movl %%ebp, %0" : "=r"(frame));
	fp = frame;
	unsigned int depth_index = 0;

	for (; (!(fp < frame)) && depth_index < BUFFER_DEPTH;
		fp = (struct frame *)((long) fp->fr_savfp)) {
		allocation_points[allocation_index][depth_index] = fp->fr_savpc;
		allocation_index = (allocation_index % (BUFFER_SIZE - 1)) + 1;
	}
#endif

	static void* (*real_malloc)(size_t) = NULL;
	if (!real_malloc)
		real_malloc = (void*(*)(size_t))dlsym(RTLD_NEXT, "malloc");

	allocatedsize += size;

	//fprintf(stdout, "%lld\n", allocatedsize);

	void *p = real_malloc(size);

	return p;
}

