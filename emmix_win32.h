/*
** emmix_win32.h
** $Id: emmix_win32.h,v 1.3 2002/03/07 06:29:28 default Exp $
**
** Modifications which are only applicable 
** to windows
**
** Author: Chui Tey
** Date  : 12-02-2002
**
** $Revision: 1.3 $
**
** $Log: emmix_win32.h,v $
** Revision 1.3  2002/03/07 06:29:28  default
** Moved routines to emmix_win.c
**
** Revision 1.2  2002/02/18 13:41:07  default
** Initial checkin
**
** Revision 1.1  2002/02/12 14:23:55  default
** Initial checkin
**
*/

#undef EM_WIN32_TEST
#ifdef EM_WIN32_TEST
#include <stdio.h>
#endif

#include <windows.h>
#include "strngutl.h"

#ifndef EM_WIN32
#define EM_WIN32

#include <process.h>
extern const char* EMMIX_EXE;
extern const char* EMMIXT_EXE;
extern const char* EMMIXS_EXE;
extern const char* EMMIXF1_EXE;
extern const char* EMMIXF2_EXE;
extern const char* NUL;
#endif

#if __WIN32__

void parseCmdLine(const char*, char *, char*, char*);
int  system(const char*);

#endif

