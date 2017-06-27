/* transpose.c */
#include <stdio.h>
#define BUFSIZE 4096
#define LINELENGTH 4096
#define MAXROWS 5000

int main(int argc, char* argv[])
{

    FILE* fp;
    char  filename[255];
    char* rows[MAXROWS];
    char  buf[BUFSIZE];
    char* strLine;
    char* token;
    int   int_token_count;
    int   total_token_count;
    int   i;
    char* szDelimiters = " \n";
    
    if (argc != 2)    
    {
        printf("Usage: %s filename\n", argv[0]);
        exit(1);
    }

    strcpy(filename, argv[1]);

    fp = fopen(filename,"r");
    if (fp == NULL)
    {
        perror("Could not open file");
        exit(1);
    }

    /* read the first line and allocate array of chars */
    fgets(buf, BUFSIZE, fp);
    token =  (char*) strtok(buf,szDelimiters);
    
    int_token_count = 0;
    while (token != NULL && int_token_count < MAXROWS)
    {
        rows[int_token_count]=(char*) malloc(LINELENGTH);
        if (rows[int_token_count] == NULL)
        {
            perror ("Memory allocation failed\n");
            exit(1);
        }
        strcpy(rows[int_token_count], token);
        int_token_count++;
        token=(char*) strtok(NULL, szDelimiters);
    }
    total_token_count = int_token_count -1;
    //printf("Total token count = %d\n", total_token_count);
    
    /* read the remainder of the lines and transpose it */
    strLine = fgets(buf, BUFSIZE, fp);
    while( strLine != NULL && !feof(fp))
    {

        token = (char*) strtok(buf," ");
        int_token_count = 0;
        while (token != NULL && int_token_count <= total_token_count)
        {

            strcat(rows[int_token_count], " ");
            strcat(rows[int_token_count], token);
            
            int_token_count++;
            token= (char*) strtok(NULL, szDelimiters);
        }

        strLine = fgets(buf, BUFSIZE, fp);
    }

    fclose(fp);

    /* write out contents to stdout */
    for (i=0; i<=total_token_count;i++) 
    {
        printf("%s\n", rows[i]);
    }

    /* free memory */
    for (i=0; i<=total_token_count; i++)
    {
        free(rows[int_token_count]);
    }

}
