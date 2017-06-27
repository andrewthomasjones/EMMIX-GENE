      PROGRAM alloc_example
C     Allocate a 1-d real array with N elements
      INTEGER N, ALLOC_ERR
      REAL ALLOCATABLE :: DATA(:)

C     You would calculate N at run time
      N = 10

C     ALLOC_ERR is set to a positive integer 
C     if an error occurs with allocation
      ALLOCATE (DATA(N), STAT= ALLOC_ERR)

      IF (ALLOC_ERR.NE.0) THEN
        WRITE (*,*) 'ERROR: Could not allocate memory'
      END IF

C     ZERO ARRAY
      DO I=1,N
        DATA(I) = I * 1.1
      END DO

C     Once you finished, deallocate the memory
      DEALLOCATE(DATA)
      END

