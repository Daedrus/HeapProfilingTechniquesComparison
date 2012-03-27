#include <stdio.h>
#include <stdint.h>
#include <dlfcn.h>

unsigned long long allocatedsize = 0;

void* malloc(size_t size)
{
	static void* (*real_malloc)(size_t) = NULL;
	if (!real_malloc)
		real_malloc = (void*(*)(size_t))dlsym(RTLD_NEXT, "malloc");

	allocatedsize += size;

	//fprintf(stdout, "%lld\n", allocatedsize);

	void *p = real_malloc(size);

	return p;
}

