#ifndef STACKLOGGER_H
#define STACKLOGGER_H

using namespace std;

class StackLogger
{
private:
	int m_size;
	int m_currpos;
	const void* stack[15];
public:
	StackLogger();
	~StackLogger();

	void enterFunction(const void*);
	void leaveFunction();
	const void* getCurrentFunction();

	const void walkStack();
};

extern StackLogger* logger;

#endif
