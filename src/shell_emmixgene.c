#include <windows.h>
#include <stdio.h>

SHELLEXECUTEINFO si;
 
int main2(int, char**);

int WINAPI WinMain(
    HINSTANCE hInstance,
    HINSTANCE hPrevInstance,
    LPSTR lpszCmdLine,
    int nCmdShow)
{
    char* ch_array[1];
    MSG   msg;
    WNDCLASS wc;
    UNREFERENCED_PARAMETER(lpszCmdLine);

    main2(0, ch_array);

    /*
    while (GetMessage(&msg, (HWND) NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage (&msg);
    }
    */

    return msg.wParam;
}

int main2(int argc, char* argv[])
{

    memset(&si, 0, sizeof(SHELLEXECUTEINFO));
    si.cbSize = sizeof(SHELLEXECUTEINFO);
    si.lpFile = "bin\\python.exe";
    si.lpParameters = "z2.py -w8080";
    si.nShow = SW_HIDE;
    si.fMask = SEE_MASK_NOCLOSEPROCESS;

    if (!ShellExecuteEx(&si))
    {
       MessageBox( NULL,
       "Failed to launch EmmixGene embedded web server",
       "EmmixGene",
       MB_OK + MB_ICONEXCLAMATION + MB_SYSTEMMODAL); 
    }
    return 1;

}
