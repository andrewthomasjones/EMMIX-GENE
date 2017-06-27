#include <stdio.h>

typedef char FILENAME[255];

int main()
{
    FILENAME tempfile[10];
    int  i;

    for (i=0; i<10; i++)
    {
        sprintf(tempfile[i], "Temp%d", i);        
    }

    for (i=0; i<10; i++)
    {
        printf("Temp file is %s\n", tempfile[i]);
    }

    return 0;
}
