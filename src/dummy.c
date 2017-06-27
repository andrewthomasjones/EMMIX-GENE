/*
#
# dummy.c
# used to simulate 
#                  select-genes
#                  cluster-genes 
#                  cluster-tissues
#
*/

#include <stdio.h>

int main(int argc, char* argv[])
{

  int i;

  if (argc!=4) {

    printf("usage: foo bar baz\n");
    return 1;

  }

  printf ("argument count: %d\n", argc);

  for (i=0; i<=argc-1; i++) {

    printf ("argv[%d] = %s\n", i, argv[i]);

  }

  return 0;

}
