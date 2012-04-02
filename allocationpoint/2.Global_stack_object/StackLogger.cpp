#include "StackLogger.h"

StackLogger::StackLogger()
	: m_size(15), m_currpos(-1)
{
}

StackLogger::~StackLogger()
{
}

void StackLogger::enterFunction(const void* f)
{
	if (m_currpos < m_size)
		stack[++m_currpos] = f;
}

void StackLogger::leaveFunction()
{
	if (m_currpos >= 0)
		m_currpos--;
}

const void* StackLogger::getCurrentFunction()
{
	if (m_currpos >= 0)
		return stack[m_currpos];
	else
		return 0;
}

const void StackLogger::walkStack()
{
	const void* tmp;
	for (int i = 0; i < m_currpos; i++)
		tmp = stack[i];
}
