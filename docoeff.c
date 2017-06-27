/* *************************************************************
**
** do-coeff - A program to work out correlation coefficients for given data.
**           As usual, the usage is "do-coeff filename number-of-rows
**           number-of-cols".  The output (to standard output)
**           consists of a number-of-rows x number-of-rows matrix
**           listing the correlation coefficient between the
**           corresponding rows.
**
** Revision history:
** $Log: docoeff.c,v $
** Revision 1.2  2002/06/10 14:10:06  default
** Refactored, and handles variable array sizes
**
** Revision 1.1  2002/06/08 13:31:37  default
** Vendor import
**
** ************************************************************ */

/* *************************************************************
** From: "Geoff McLachlan" <gjm@maths.uq.edu.au>
** To: <teyc@cognoware.com>
** 
** chui, it was good to meet yesterday afternoon,
** as it has served to focus just what we hope to provide with EMMIX-GENE 
** and jess'
** contribution on this aspect is very valuable.
**
** i am enclosing an damended version of do-coeff.c (which i am now
** calling doc.c)
**
** geoff
** ************************************************************ */

/* work out correlation coefficients for given data */

// #define MAXROWS 200
// #define MAXCOLS 120

#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/* *************************************************************
** double** calloc_double2( int rows, int cols, size_t size)
** Allocates a two dimensional array in a contiguous block
** of memory
** ************************************************************ */
double **
calloc_double2 (int rows, int cols)
{
  double **temp = NULL;
  int i = 0;

  temp = malloc (rows * sizeof (double));
  if (temp == NULL)
    {
      return NULL;
    }

  temp[0] = calloc (rows * cols, sizeof (double));
  if (temp[0] == NULL)
    {
      free (temp);
      return NULL;
    }

  for (i = 1; i < rows; i++)
    {
      temp[i] = temp[i - 1] + cols;
    }

  return temp;
}

void free_double2(double** array)
{
    free(array[0]);
    free(array);
}

/* *************************************************************
** read_data()
** Purpose:
**     reads data from filename into an array
** ************************************************************ */
int
read_data (char *filename, int rows, int cols, double ***y, double ***sarray)
{

  FILE *f;
  int i = 0, j = 0;
  int err = 0;
  char msg[1024];
  double **data_array;
  double **corr_array;

  /* Allocate array for input file */
  data_array = calloc_double2 (rows, cols);
  corr_array = calloc_double2 (rows, rows);
  if (data_array == NULL)
    {
      fprintf (stderr, "The number of rows and columns are too large.\n");
      return 1;
    }

  /* Allocate array for calculation of correlation */
  f = fopen (filename, "r");
  if (f == NULL)
    {
      sprintf (msg, "Could not open %s", filename);
      perror (msg);
      return 1;
    };

  for (j = 0; j < rows; j++)
    {
      for (i = 0; i < cols; i++)
       {
         if (feof (f))
           {
             err = 1;
             goto err_eof;
           }
         fscanf (f, "%lf", &(data_array[j][i]));
       }
    }
  fclose (f);

  /* return the memory location of the array */
  *y = data_array;
  *sarray = corr_array;

  return 0;

err_eof:

  sprintf (msg, "EOF reached after reading %d rows, %d columns\n", j, i);
  perror (msg);
  fclose (f);
  free (data_array);
  free (corr_array);
  return err;
}

int
main (int argc, char **argv)
{
  double sum;
  int i = 0, j = 0;
  int rows = 0, cols = 0;
  int err = 0;
  char datafile[255];

  // double y[MAXROWS][MAXCOLS];
  // double sarray[MAXROWS][MAXROWS];
  double **y = NULL;
  double **sarray = NULL;

  if (argc != 4)
    {
      printf ("Usage: %s filename #rows #cols\n", argv[0]);
      exit (EXIT_FAILURE);
    }

  strcpy (datafile, argv[1]);
  rows = atoi (argv[2]);
  cols = atoi (argv[3]);

  /* read data into y[][] */
  err = read_data (datafile, rows, cols, &y, &sarray);
  if (err)
    {
      exit (EXIT_FAILURE);
    }

  /* compute correlation and place result in sarray[][] */
  for (i = 0; i < rows; i++)
    {
      for (j = 0; j < rows; j++)
       {
         int x;
         sum = 0.0;
         for (x = 0; x < cols; x++)
           {
             sum += y[i][x] * y[j][x];
           }
         sarray[i][j] = sum / (cols - 1);
       }
    }

  /* output sarray[][] */
  for (i = 0; i < rows; i++)
    {
      for (j = 0; j < rows; j++)
       {
         printf ("%2.5f ", sarray[i][j]);
         /* 2 places before dp, 5 places after = */
       }
      printf ("\n");
    }

  free_double2(y);
  free_double2(sarray);
  return 0;

}
