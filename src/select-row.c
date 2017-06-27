/* select-row.c
   returns a given row in a file 
*/

#include <stdio.h>

int main(int argc, char* argv[])
{
    char  filename[255];
    char  buf[4096];
    int   row;
    int   i;
    FILE* fd;
    
    if (argc != 3)
    {
        printf("Usage: %s filename row\n", argv[0]);
        exit(1);
    }
    
    strcpy(filename, argv[1]);
    row=atoi(argv[2]);

    fd=fopen(filename, "r");
    if (!fd)
    {
        perror("Could not open input file\n");
        exit(1);
    }

    for (i=1; i<=row; i++)
    {
        fgets(buf, 4096, fd);
        if (strlen(buf)==0)       
            break;
        if (i==row)
            printf(buf);
        
    }

    fclose(fd);
    return 1;
}

