/* emmix_win32.c
** Win32 specific routines for emmix
**
*/

#define EM_WIN32

#if __WIN32__
#include <windows.h>
#include <winuser.h>
#include <process.h>
const char* EMMIX_EXE = "EMMIX";
const char* EMMIXT_EXE = "EMMIX-t";
const char* EMMIXS_EXE = "EMMIX-spher";
const char* EMMIXF1_EXE = "EMMIX-f1";
const char* EMMIXF2_EXE = "EMMIX-f2";
const char* NUL = "NUL";
#else
const char* EMMIX_EXE = "./EMMIX";
const char* EMMIXT_EXE = "./EMMIX-t";
const char* EMMIXS_EXE = "./EMMIX-spher";
const char* EMMIXF1_EXE = "./EMMIX-f1";
const char* EMMIXF2_EXE = "./EMMIX-f2";
const char* NUL = "/dev/null";
#endif

int system(const char*);
void parseCmdLine(const char*, char*, char*, char* );

int system(const char* cmdline)
{

    SECURITY_ATTRIBUTES sa;
    STARTUPINFO         si;
    PROCESS_INFORMATION pi;
    BOOL                success;

    char cmd[1024];
    char filein[1024];
    char fileout[1024];
    
    /* Parse cmdline for redirected input and output */
    parseCmdLine(cmdline, cmd, filein, fileout);
    
    ZeroMemory(&sa, sizeof(SECURITY_ATTRIBUTES));
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;
    sa.lpSecurityDescriptor = NULL;

    memset(&si, 0, sizeof(STARTUPINFO));
    si.cb = sizeof(STARTUPINFO);
    si.dwFlags = STARTF_USESTDHANDLES;

    if (*filein)
    {
        si.hStdInput = CreateFile(
           filein,
           GENERIC_READ,
           0,                   /* File share mode */
           &sa,                 /* Security attributes */
           OPEN_EXISTING,
           FILE_ATTRIBUTE_NORMAL,
           NULL
        );
        if (!si.hStdInput) {
           printf("CreateFile %s failed!\n", filein);
        }
    }   
    
    /* strcpy (fileout, "foobarout"); */
    if (*fileout && strcasecmp(fileout,"NUL")!=0)
    {
        si.hStdOutput = CreateFile(
           fileout,
           GENERIC_WRITE,
           0,                   /* File share mode */
           &sa,                 /* Security attributes */
           CREATE_ALWAYS,
           FILE_ATTRIBUTE_NORMAL,
           NULL
        );
        if (!si.hStdOutput) {
           printf("CreateFile %s failed!\n", fileout);
        }
    }
    
    if (*filein) printf("File In:%s.\n", filein);
    if (*fileout) printf("File Out:%s.\n", fileout);

    success = CreateProcess(
      NULL,
      cmd,
      NULL,
      NULL,
      TRUE,                 /* inherit handles */
      DETACHED_PROCESS,     /* DETACHED_PROCESS has no console */
      NULL,                 /* environment */
      NULL,                 /* current directory */
      &si,                  /* startupinfo */
      &pi                   /* processinformation */
    );

    /* Wait until process completes */
    printf("Waiting for process %s to complete\n", cmdline );
    WaitForSingleObject( pi.hProcess, INFINITE);
    printf("Process completed\n");
    
    CloseHandle (si.hStdInput);
    CloseHandle (si.hStdOutput);
    
    /* fixme */
    return 1;
}

/*
**  Parameters:
**  cmdLine     [in]    original command line eg. foo moo < bar > baz
**  cmd         [out]   foo moo
**  filein      [out]   bar (or NULL)
**  fileout     [out]   baz (or NULL)
*/  
void parseCmdLine(const char* cmdLine, char* cmd, char* filein, char* fileout)
{
    
    char* charGT; char* charLT;

    memset(cmd, 0, 1024);
    memset(filein, 0, 1024);
    memset(fileout, 0, 1024);

    /* copy over commandline up to < or > */
    charGT = strstr(cmdLine, ">");
    charLT = strstr(cmdLine, "<");
    if (charGT > (cmdLine + 1) && charGT < charLT)
    {
        strncpy(cmd, cmdLine, charGT - cmdLine);
        strncpy(fileout, charGT + 1, charLT - charGT - 1);
        strcpy(filein, charLT + 1);
    }
    else if (charLT > (cmdLine + 1) && charLT < charGT)
    {
        
        strncpy(cmd, cmdLine, (charLT - cmdLine));
        strncpy(filein, charLT + 1, charGT - charLT - 1);
        strcpy(fileout, charGT + 1);
    }
    else if (charGT > (cmdLine + 1) && charLT == 0)
    {
        strncpy(cmd, cmdLine, charGT - cmdLine);
        strcpy(fileout, charGT + 1);
    }
    else if (charLT > (cmdLine + 1) && charGT == 0)
    {
        strncpy(cmd, cmdLine, (charLT - cmdLine));
        strcpy(filein, charLT + 1);
    }
        
   if (*filein) { ltrim(filein); rtrim(filein); };
   if (*fileout) { ltrim(fileout); rtrim(fileout); };

}

void perror(const char* msg)
{
    MessageBoxEx(
        0,      /* hWnd - no owner window */
        msg,    /* lpText                 */
        "EmmixGene",    /* lpCaption      */
        MB_OK,
        MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_AUS));
}

#if EM_WIN32_TEST

void report(char* cmdLine,
            char* cmd,
            char* filein,
            char* fileout)
{
    printf("cmdLine: %s\n", cmdLine);
    printf("cmd    : %s\n", cmd);
    printf("filein : %s\n", filein);
    printf("fileout: %s\n", fileout);
    printf("-------------\n");

}

int main(int argc, char* argv[])
{
    char* cmdLine;
    char cmd[1024];
    char filein[1024];
    char fileout[1024];

    cmdLine = "foo bar < baz1 > baz2";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);

    cmdLine = "foo bar <baz1 baz2 >baz3 baz4";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);

    cmdLine = "foo bar > baz1 < baz2";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);
    
    cmdLine = "foo bar >baz1 baz2 <baz3 baz4";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);

    cmdLine = "foo bar >baz1 baz2";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);

    cmdLine = "foo bar <baz3 baz4";
    parseCmdLine(cmdLine, cmd, filein, fileout);
    report(cmdLine, cmd, filein, fileout);

    return 0;
}
#endif

