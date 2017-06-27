#define LINE_LENGTH 1000	/* max length of each line in microarray data */
#define MAX_GENES 2200		/* max number of genes in microarray data */
#define MAX_TISSUES 75		/* max number of tissues in microarray data */
#define MAX_ENTRY_LENGTH 20	/* max length of any single entry in the array */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* filename, number of clusters, number of rows, number of
   vars/dimensions, number of factor
   dimensions, number of groups, number of random & k-means starts,
   random seeds */
int f1, g, r, k, s1, s2, s3, clus;

void call_emfac (char **argv, int n, int p);
void call_emface (char **argv, int n, int p);
void call_emmix (char **argv, int n, int p);

main (int argc, char **argv)
{
  FILE *f;
  int n;			/* number of rows - 2nd argument */
  int p;			/* number of cols - 3rd argument */
  int tmp, i, j, opt;
  char s[MAX_GENES][MAX_TISSUES][MAX_ENTRY_LENGTH];
  char t[LINE_LENGTH];		/* max filename length */
  if (argc != 4)
    {
      printf
	("usage: cluster-tissues microarray-filename number-of-rows number-of-columns\n");
      exit (1);
    }
  n = atoi (argv[2]);
  p = atoi (argv[3]);
  printf ("Enter 1 to use factor analyzers, 2 to use EMMIX\n");
  scanf ("%d", &opt);
  if (opt == 1) { printf ("How many factors?\n");
  scanf ("%d", &f1); }
  printf ("How many components?\n");
  scanf ("%d", &g);
  printf ("How many random starts?\n");
  scanf ("%d", &r);
  printf ("How many k-means starts?\n");
  scanf ("%d", &k);
  printf ("Random Seed 1?\n");
  scanf ("%d", &s1);
  printf ("Random Seed 2?\n");
  scanf ("%d", &s2);
  printf ("Random Seed 3?\n");
  scanf ("%d", &s3);

  f = fopen (argv[1], "r");
  for (i = 0; i < n; i++)
    for (j = 0; j < p; j++)
      fscanf (f, "%s", s[i][j]);
  fclose (f);

  sprintf (t, "%s.trans", argv[1]);
  f = fopen (t, "w");
  for (i = 0; i < p; i++)
    {
      for (j = 0; j < n; j++)
	{
	  fprintf (f, "%s ", s[j][i]);
	}
      fprintf (f, "\n");
    }
  fclose (f);

  tmp = n;
  n = p;
  p = tmp;

  if (opt == 1)
  { if (n > p)
    call_emfac (argv, n, p);
  else
    call_emface (argv, n, p); 
  }
  else
    call_emmix (argv, n, p);
  sprintf (t, "%s.trans", argv[1]);
  unlink(t);
}

void
call_emfac (char **argv, int n, int p)
{
  FILE *f;
  int i, j;
  char s[LINE_LENGTH];
  sprintf (s, "tmp.%d", getpid ());
  f = fopen (s, "w");
  fprintf (f, "%s.trans\n", argv[1]);
  fprintf (f, "%s.out\n", argv[1]);
  fprintf (f, "%s.m\n", argv[1]);
  fprintf (f, "%s.mod\n", argv[1]);
  fprintf (f, "%d\n", n);
  fprintf (f, "%d\n", p);
  fprintf (f, "%d\n", p);
  fprintf (f, "0\n");		/* DON'T CLUSTER COLUMNS */
  fprintf (f, "%d\n", f1);
  fprintf (f, "0\n");
  fprintf (f, "%d\n", g);
  fprintf (f, "2\n3\n");
  fprintf (f, "%d\n100\n%d\n", r, k);
  fprintf (f, "1\n0\n%d\n%d\n%d\n", s1, s2, s3);
  fclose (f);
  sprintf (s, "./EMMIX-f1 < tmp.%d > /dev/null", getpid ());
  system (s);
  sprintf (s, "%s.out", argv[1]);
  f = fopen (s, "r");
  while (!strstr (s, "Implied Grouping"))
    fgets (s, LINE_LENGTH, f);
  for (i = 0; i < n; i++)
    {
      fscanf (f, "%d", &j);
      printf ("%d  ", j);
      if (i > 0 && (i % 10) == 9)
	printf ("\n");
    }
  printf ("\n");
  sprintf (s, "%s.out", argv[1]);
  unlink (s);
  sprintf (s, "%s.m", argv[1]);
  unlink (s);
  sprintf (s, "%s.mod", argv[1]);
  unlink (s);
  sprintf (s, "tmp.%d", getpid ());
  unlink (s);
}

void
call_emface (char **argv, int n, int p)
{
  FILE *f;
  int i, j;
  char s[LINE_LENGTH];
  sprintf (s, "tmp.%d", getpid ());
  f = fopen (s, "w");
  fprintf (f, "%s.trans\n", argv[1]);
  fprintf (f, "%s.out\n", argv[1]);
  fprintf (f, "%s.m\n", argv[1]);
  /*fprintf(f,"%s.mod\n",argv[1]); */
  fprintf (f, "%d\n", n);
  fprintf (f, "%d\n", p);
  fprintf (f, "%d\n", p);
  /*fprintf(f,"0\n"); */
  fprintf (f, "%d\n", f1);
  fprintf (f, "0\n");
  fprintf (f, "%d\n", g);
  fprintf (f, "2\n3\n");
  fprintf (f, "%d\n100\n%d\n", r, k);
  fprintf (f, "0\n0\n%d\n%d\n%d\n", s1, s2, s3);
  fclose (f);
  sprintf (s, "./EMMIX-f2 < tmp.%d > /dev/null", getpid ());
  system (s);
  sprintf (s, "%s.out", argv[1]);
  f = fopen (s, "r");
  while (!strstr (s, "Final Allocation"))
    fgets (s, LINE_LENGTH, f);
  fgets (s, LINE_LENGTH, f);
  for (i = 0; i < n; i++)
    {
      fscanf (f, "%d", &j);
      printf ("%d  ", j);
      if (i > 0 && (i % 10) == 9)
	printf ("\n");
    }
  printf ("\n");
  sprintf (s, "%s.out", argv[1]);
  unlink (s);
  sprintf (s, "%s.m", argv[1]);
  unlink (s);
  sprintf (s, "tmp.%d", getpid ());
  unlink (s);
}

void call_emmix (char **argv, int n, int p)
{
  FILE *f;
  int i, j;
  char s[LINE_LENGTH];
  sprintf (s, "tmp.%d", getpid ());
  f = fopen (s, "w");
  fprintf (f, "2\n");
  fprintf (f, "%s\n", argv[1]);
  fprintf (f, "%s.out\n", argv[1]);
  fprintf (f, "%d\n", n);
  fprintf (f, "%d\n", p);
  fprintf (f, "%d\n", p);
  fprintf (f, "%d\n", g);
  fprintf (f, "2\n3\n");
  fprintf (f, "%d\n100\n%d\nn\n", r, k);
  fprintf (f, "%d\n%d\n%d\n", s1, s2, s3);
  fclose (f);
  sprintf (s, "./EMMIX-t < tmp.%d > /dev/null", getpid ());
  system (s);
  sprintf (s, "%s.out", argv[1]);
  f = fopen (s, "r");
  while (!strstr (s, "Implied grouping"))
    fgets (s, LINE_LENGTH, f);
  fgets (s, LINE_LENGTH, f);
  for (i = 0; i < n; i++)
    {
      fscanf (f, "%d", &j);
      printf ("%d  ", j);
      if (i > 0 && (i % 10) == 9)
	printf ("\n");
    }
  printf ("\n");
  sprintf (s, "%s.out", argv[1]);
  unlink (s);
  sprintf (s, "tmp.%d", getpid ());
  unlink (s);
}

