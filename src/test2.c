#include <stdio.h>
#include <string.h>

char* basename(char *path)
{
    char *save_ptr; 
    char *next_token;
    char *prev_token;
    char *delimiter = "\\";
    char *new_string;

    if (path == NULL) return NULL;
   
    new_string = (char*) malloc(strlen(path));
    strcpy(new_string, path);

    next_token = strtok(new_string, delimiter);
    while (next_token != NULL)
    {
        prev_token = next_token;
        next_token = strtok(0, delimiter);
    }
        
    free(new_string);
    return path + ((long) prev_token - (long) new_string);
}

char* dirname(char* path)
{
    char* new_string;
    int   new_length;
    int   length;

    if (path==NULL || strlen(path)==0 || strcmp(path, ".")==0 || 
        strchr(path, "\\") == NULL)
    {
        new_string = malloc(2);
        strcpy(new_string, ".");
        return new_string;
    }
    
    length = strlen(basename(path));
    new_length = strlen(path) -length + 1;
    new_string = malloc(new_length);
    memcpy(new_string, path, new_length);
    new_string[new_length-1]= 0;
    return new_string;
}

void test(char* prog)
{

   char *basedirname;
    
   printf("Base name of %s is \"%s\"\n", prog, basename(prog));
   basedirname = dirname(prog);
   printf("Base Directory = '%s'\n\n", basedirname) ;
   free(basedirname);
}

int main(int argc, char** argv)
{
   char *prog;
   
   prog="C:\\program files\\emmixgene\\emmixgene.exe";
   test(prog);

   prog="C:\\program files\\emmixgene\\";
   test(prog);

   prog="struck.exe";
   test(prog);
   
   prog=".";
   test(prog);
   
   printf("Sanity check: %s\n", prog);
   return 0;
}
