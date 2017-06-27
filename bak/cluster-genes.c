#define LINE_LENGTH 1000	/* max length of each line in microarray data */
#define MAX_GENES 2200		/* max number of genes in microarray data */
#define MAX_TISSUES 75		/* max number of tissues in microarray data */
#define MAX_GROUPS 100		/* max number of groups to split into */
#define MAX_ENTRY_LENGTH 20	/* max length of any single entry in the array */

#include <unistd.h>		/* getpid, unlink */
#include <stdlib.h>		/* exit */
#include <stdio.h>		/* printf, scanf */
#include <string.h>		/* strtok */

void call_emmix (char **argv, char *t, float *tl, int *sm, int *er, int col,
		 int g);
void call_emd (char **argv, int col, int g, int clus, int genecount);
void strip_cr (char s[LINE_LENGTH], char t[LINE_LENGTH]);

struct tab
{
  int nu;
  int count;
  float tl;
  char s[LINE_LENGTH];
};


int r, k, s1, s2, s3;		/* random starts, k-means starts, seeds 1 to 3 */

int reord;
int
tabcompare (const void *p1, const void *p2)
{
  float i = (*((struct tab *) p1)).tl;
  float j = (*((struct tab *) p2)).tl;
  if (i < j)
    return 1;
  if (i > j)
    return -1;
  return 0;
}
  float b1,b2;

main (int argc, char **argv)
{
  int row;			/* 2nd argument */
  int col;			/* 3rd argument */
  int g;			/* 4th argument */
  int x;			/* counter */
  int i;			/* another counter */
  int rc, r1, k1, clus;
  int genecount = 0;
  char s[LINE_LENGTH];
  char sg[MAX_GENES][LINE_LENGTH];	/* each line up to LINE_LENGTH chars long, max MAX_GENES lines */

  FILE *f, *f2, *f3, *f4;
  if (argc != 4)
    {
      printf
	("usage: cluster-genes microarray-filename number-of-rows number-of-columns\n");
      exit (1);
    }
  col = atoi (argv[3]);
  row = atoi (argv[2]);
  g = 1;
  /* rm -f error.$1.$$ log.$1.$$ smaller.$1.$$ input1.$$ */
  /* sprintf(s,"error.%d",getpid());
     unlink(s);
     sprintf(s,"log.%d",getpid());
     unlink(s);
     sprintf(s,"smaller.%d",getpid());
     unlink(s); */
  printf
    ("How many random starts for the fitting of normal components to group means?\n");
  scanf ("%d", &r);
  printf
    ("How many k-means starts for the fitting of normal components to group means?\n");
  scanf ("%d", &k);
  printf
    ("How many random starts for the fitting of common spherical components to the selected genes?\n");
  scanf ("%d", &r1);
  printf
    ("How many k-means starts for the fitting of common spherical components to the selected genes?\n");
  scanf ("%d", &k1);
  printf ("How many groups into which to cluster the selected genes?\n");
  scanf ("%d", &clus);

  /* printf ("Enter threshold for likelihood ratio statistic:\n"); 
  scanf ("%d", &B1); */
  printf ("Enter threshold for minimum cluster size:\n");       /* s_{min} cutoff */
  scanf ("%d", &b2);


  printf ("Enter random seed 1:\n");
  scanf ("%d", &s1);
  printf ("Enter random seed 2:\n");
  scanf ("%d", &s2);
  printf ("Enter random seed 3:\n");
  scanf ("%d", &s3);
  printf
    ("Do you wish to reorder the tissues as clustered on\nbasis of fitted group means?\n");
  scanf ("%s", s);
  if (s[0] == 'y' || s[0] == 'Y')
    reord = 1;
  else
    reord = 0;

  sprintf (s, "input1.%d", getpid ());
  f = fopen (s, "w");
  if (!f)
    perror (s);
  fprintf (f, "2\n");
  fprintf (f, "%s\n", argv[1]);	/* input file */
  fprintf (f, "%s.tmp\n", argv[1]);
  fprintf (f, "%sm\n", argv[1]);	/* matlab file */
  fprintf (f, "%d\n", row);
  fprintf (f, "%d\n", col);
  fprintf (f, "0\n");
  fprintf (f, "%d\n", clus);
  fprintf (f, "5\n3\n");	/* option 5, eq, option 3, random starts */
  fprintf (f, "%d\n100\n%d\n", r1, k1);	/* rand starts, 100%, k-means */
  fprintf (f, "n\n%d\n%d\n%d\n", s1, s2, s3);	/* rand seeds */
  fclose (f);

  call_emd (argv, col, g, clus, row);

  /* clean up */
  sprintf (s, "input1.%d", getpid ());
  unlink (s);
  sprintf (s, "input2.%d", getpid ());
  unlink (s);
  sprintf (s, "input3.%d", getpid ());
  unlink (s);
  sprintf (s, "input4.%d", getpid ());
  unlink (s);
  sprintf (s, "%s.tmp", argv[1]);
  unlink (s);
  sprintf (s, "out1.%d", getpid ());
  unlink (s);
  sprintf (s, "out2.%d", getpid ());
  unlink (s);
  sprintf (s, "%sm", argv[1]);
  unlink (s);
  sprintf (s, "tmp.%d", getpid ());
  unlink (s);
}

void
call_emd (char **argv, int col, int g, int clus, int genecount)
{
  char s[LINE_LENGTH];
  char t[LINE_LENGTH];
  int grea[MAX_GROUPS][MAX_TISSUES];	/* up to MAX_GROUPS group means, up to MAX_TISSUES samples per mean */

  struct tab gl[MAX_GROUPS];
  int gmap[MAX_GROUPS];		/* mapping between group numbers */
  FILE *f, *f2, *f3, *f4;
  int i, j, sm, er,x;
  float tl;
  sprintf (s, "./EMMIX-spher < input1.%d >/dev/null", getpid ());
  system (s);

  sprintf (s, "%s.tmp", argv[1]);
  f = fopen (s, "r");
  if (!f)
    perror (s);
  /* go down to "Estimated mean...for each component" to get group means */
  while ((!strstr (s, "Estimated mean") || !strstr (s, "each")) && !feof (f))
    fgets (s, LINE_LENGTH, f);
  if (feof (f))
    {
      printf ("failed to find start\n");
      exit (1);
    }
  sprintf (s, "%s_groupmeans", argv[1]);
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);
  for (j = 0; j < clus; j++)
    {
      for (i = 0; i < col; i++)
	{
	  fscanf (f, "%s", s);
	  fprintf (f2, "%s ", s);
	}
      fprintf (f2, "\n");
    }
  fclose (f2);
  fclose (f);

  sprintf (s, "%s_groupmeans", argv[1]);
  f = fopen (s, "r");
  if (!f)
    perror (s);

  for (j = 0; j < clus; j++)
    fgets (gl[j].s, LINE_LENGTH, f);
  fclose (f);

  sprintf (s, "%s_groupmeans", argv[1]);
  f4 = fopen (s, "r");
  if (!f4)
    perror (s);
  /* calculate -2 log \lambda for group means */
  for (i = 0; i < clus; i++)
    {
      /* get s */
      fgets (s, LINE_LENGTH, f4);
      strip_cr (s, t);

  sprintf (s, "input1.%d", getpid ());
  f = fopen (s, "w");
  if (!f)
    perror (s);
  sprintf (s, "input3.%d", getpid ());
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);
  fprintf (f, "2\n");		/* echo 2 >> input1.$$ */
  fprintf (f, "tmp.%d\n", getpid ());	/* echo tmp.$$ >> input1.$$ */
  fprintf (f, "out1.%d\n", getpid ());	/* echo out1.$$ >> input1.$$ */
  fprintf (f, "%d\n", col);	/* echo $3 >> input1.$$ */
  fprintf (f, "1\n");		/* echo 1 >> input1.$$ */
  fprintf (f, "1\n");		/* echo 1 >> input1.$$ */

  fprintf (f2, "2\n");		/* echo 2 >> input1.$$ */
  fprintf (f2, "tmp.%d\n", getpid ());	/* echo tmp.$$ >> input1.$$ */
  fprintf (f2, "out1.%d\n", getpid ());	/* echo out1.$$ >> input1.$$ */
  fprintf (f2, "%d\n", col);	/* echo $3 >> input1.$$ */
  fprintf (f2, "1\n");		/* echo 1 >> input1.$$ */
  fprintf (f2, "1\n");		/* echo 1 >> input1.$$ */

  fprintf (f, "1\ny\n9\n2\n.5\n0\n");

  fprintf (f2, "%d\n2\n3\n%d\n100\n%d\ny\n9\n2\n", 2, r, k);
  x = 0;
  while (x++ < 2)
    fprintf (f2, "1\n");
  fprintf (f2, "0\n%d\n%d\n%d\n", s1, s2, s3);

  fclose (f);
  fclose (f2);

  sprintf (s, "input2.%d", getpid ());
  f = fopen (s, "w");
  if (!f)
    perror (s);
  sprintf (s, "input4.%d", getpid ());
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);

  fprintf (f, "2\n");
  fprintf (f, "tmp.%d\n", getpid ());
  fprintf (f, "out2.%d\n", getpid ());
  fprintf (f, "%d\n", col);
  fprintf (f, "1\n");
  fprintf (f, "1\n");
  fprintf (f, "%d\n", 1 + 1);
  fprintf (f, "2\n");
  fprintf (f, "3\n");
  fprintf (f, "%d\n", r);
  fprintf (f, "100\n");
  fprintf (f, "%d\n", k);
  fprintf (f, "y\n");
  fprintf (f, "9\n");
  fprintf (f, "2\n");

  fprintf (f2, "2\n");
  fprintf (f2, "tmp.%d\n", getpid ());
  fprintf (f2, "out2.%d\n", getpid ());
  fprintf (f2, "%d\n", col);
  fprintf (f2, "1\n");
  fprintf (f2, "1\n");
  fprintf (f2, "%d\n", 2 + 1);
  fprintf (f2, "2\n");
  fprintf (f2, "3\n");
  fprintf (f2, "%d\n", r);
  fprintf (f2, "100\n");
  fprintf (f2, "%d\n", k);
  fprintf (f2, "y\n");
  fprintf (f2, "9\n");
  fprintf (f2, "2\n");

  x = 0;
  while (x++ <= 1)
    {
      fprintf (f, "1\n");
    }
  x = 0;
  while (x++ <= 2)
    {
      fprintf (f2, "1\n");
    }

  fprintf (f, "0\n");
  fprintf (f, "%d\n%d\n%d\n", s1, s2, s3);

  fprintf (f2, "0\n");
  fprintf (f2, "%d\n%d\n%d\n", s1, s2, s3);
  fclose (f);
  fclose (f2);

      call_emmix (argv, t, &tl, &sm, &er, col, g);

      if (sm < b2)
              call_emmix (argv, t, &tl, &sm, &er, col, g + 1);

      /* extract grouping for possible rearrangement */
      sprintf (s, "out2.%d", getpid ());
      f2 = fopen (s, "r");
      if (!f2)
	perror (s);
      while (!strstr (s, "Implied") && !feof (f2))
	fgets (s, LINE_LENGTH, f2);
      for (j = 0; j < col; j++)
	fscanf (f2, "%d", &(grea[i][j]));
      fclose (f2);

      gl[i].nu = i;
      gl[i].tl = tl;

      /*fgets (s, LINE_LENGTH, f); */
    }
  fclose (f4);
  qsort ((void *) gl, clus, sizeof (struct tab), tabcompare);

  for (i = 0; i < clus; i++)
    gmap[gl[i].nu] = i;

  /* open .cut file */
  /*sprintf (s, "%s.cut", argv[1]); */
  f4 = fopen (argv[1], "r");
  if (!f4)
    perror (argv[1]);

  /* open matlab file */
  sprintf (s, "%sm", argv[1]);
  f2 = fopen (s, "r");
  if (!f2)
    perror (s);

  /* wipe out group%d files */
  for (i = 0; i < clus; i++)
    {
      sprintf (s, "%s_group%d", argv[1], i+1);
      unlink (s);
      sprintf (s, "%s_list%d", argv[1], i+1);
      unlink (s);
    }

  for (i = 0; i < clus; i++)
    gl[i].count = 0;
  /* go through each a line at a time, writing lines to _group%d files */
  for (i = 0; i < genecount; i++)
    {
      FILE *f3, *f5, *f6;
      float f;
      int j,tmp,tmp2,x;
      fscanf (f2, "%d", &j);
      sprintf (s, "%s_list%d", argv[1], gmap[j - 1]+1);
      f5 = fopen (s, "a");
      if (!f5)
	perror (s);

      sprintf (s, "%s.sstats", argv[1]);
      f6 = fopen(s, "r");
      if (!f6) perror(s);
      /* scan through i lines */
      for (x = 0; x < i; x++)
          /*fscanf(f6,"%s",s);*/ fgets(s, LINE_LENGTH, f6);
      fscanf(f6,"%d %f %d",&tmp,&f,&tmp2);
      fclose(f6);

      fprintf (f5, "%d %f\n", i + 1, f); /* write number and -2ll */
      
      fclose (f5);
      gl[gmap[j - 1]].count++;
      sprintf (s, "%s_group%d", argv[1], gmap[j - 1]+1);
      f3 = fopen (s, "a");
      if (!f3)
	perror (s);
      fgets (s, LINE_LENGTH, f4);
      if (!reord)
	fputs (s, f3);
      else
	{
	  char u[MAX_TISSUES][MAX_ENTRY_LENGTH],
	    v[MAX_TISSUES][MAX_ENTRY_LENGTH];
	  int k, m, l = 0;
	  strcpy (u[0], strtok (s, " "));
	  for (m = 1; m < col; m++)
	    strcpy (u[m], strtok (0, " "));
	  /* remove '\n' from u[col-1] */
	  u[col - 1][strlen (u[col - 1]) - 1] = 0;
	  for (k = 1; k <= g + 1; k++)
	    for (m = 0; m < col; m++)
	      if (grea[j - 1][m] == k)
		strcpy (v[l++], u[m]);
	  for (m = 0; m < col; m++)
	    fprintf (f3, "%s ", v[m]);
	  fprintf (f3, "\n");
	}
      fclose (f3);
    }
  fclose (f4);
  fclose (f2);
  sprintf (s, "%s.gstats", argv[1]);
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);
  for (i = 0; i < clus; i++)
    fprintf (f2, "%d %d %f\n", i+1, gl[i].count, gl[i].tl);
  fclose (f2);

  sprintf (s, "%s_groupmeans", argv[1]);
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);
  for (i = 0; i < clus; i++)
    fprintf (f2, "%s", gl[i].s);
  fclose (f2);
}

void
call_emmix (char **argv, char *t, float *tl, int *sm, int *er, int col, int g)
{
  FILE *f2;
  float fl1, fl2;
  int group1[MAX_TISSUES], group2[MAX_TISSUES];
  int comp[MAX_TISSUES], x, y = 0, a1, a2, i;
  char s[LINE_LENGTH];

  sprintf (s, "tmp.%d", getpid ());
  f2 = fopen (s, "w");
  if (!f2)
    perror (s);
  fputs (t, f2);
  fprintf (f2, "\n");
  fclose (f2);

  if (g == 1)
    {
      sprintf (s, "./EMMIX-t < input1.%d > /dev/null", getpid ());
      system (s);
      sprintf (s, "./EMMIX-t < input2.%d > /dev/null", getpid ());
      system (s);
    }
  else
    {
      sprintf (s, "./EMMIX-t < input3.%d > /dev/null", getpid ());
      system (s);
      sprintf (s, "./EMMIX-t < input4.%d > /dev/null", getpid ());
      system (s);
    }
  /* printf("%d\n",i); */

  sprintf (s, "out1.%d", getpid ());
  f2 = fopen (s, "r");
  if (!f2)
    perror (s);
  while (!strstr (s, "Log-L") && !feof (f2))
    fgets (s, LINE_LENGTH, f2);
  a1 = sscanf (s, " Final Log-Likelihood is %f", &fl1);
  fclose (f2);

  sprintf (s, "out2.%d", getpid ());
  f2 = fopen (s, "r");
  if (!f2)
    perror (s);
  while (!strstr (s, "Log-L") && !feof (f2))
    fgets (s, LINE_LENGTH, f2);
  a2 = sscanf (s, " Final Log-Likelihood is %f", &fl2);
  fclose (f2);
  if (a1 && a2)
    *tl = 2.0 * (fl2 - fl1);
  else
    {
      *tl = -100;
      *sm = -100;
      *er = -100;
      return;
    }

  /* calculate error rate */
  /*sprintf (s, "%s-group", argv[1]);
     f2 = fopen (s, "r");
     if (!f2) perror(s);
     for (i = 0; i < col; i++)
     fscanf (f2, "%d", &group1[i]);
     fclose (f2); */

  sprintf (s, "out2.%d", getpid ());
  f2 = fopen (s, "r");
  if (!f2)
    perror (s);
  while (!strstr (s, "Implied") && !feof (f2))
    fgets (s, LINE_LENGTH, f2);
  for (i = 0; i < col; i++)
    fscanf (f2, "%d", &group2[i]);

  fclose (f2);
  *er = 0;
  /* for (i = 0; i < col; i++)
     if (group1[i] != group2[i])
     (*er)++;
     if (col - *er < *er)
     *er = col - *er; */

  memset (comp, 0, sizeof (comp));
  for (i = 0; i < col; i++)
    comp[group2[i]]++;
  *sm = 9999;
  for (i = 1; i <= g + 1; i++)
    if (comp[i] < *sm)
      *sm = comp[i];
}

void
strip_cr (char s[LINE_LENGTH], char t[LINE_LENGTH])
{
  int x, y;
  char last;
  y = 0;
  for (x = 0; x < strlen (s); x++)
    {
      last = s[x];
      if (s[x] == ' ' || s[x] == '\t')
	{
	  t[y++] = '\n';
	  continue;
	}
      if (s[x] == '\n' && last == '\n')
	continue;
      t[y++] = s[x];
    }
  t[y] = 0;			/* NUL character to end string */
}
