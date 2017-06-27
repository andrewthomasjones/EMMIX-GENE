      PROGRAM TST_ARR
C     Test program 
C     Checks variable dimensioning
C     and passing arrays
C     CGT 2002 MARCH
      IMPLICIT NONE
      REAL MYARR(10,15)
      REAL T2(10);
      INTEGER I,J
      DO 100 I=1,10
        DO 200 J=1,15
          MYARR(I,J)=REAL(I)*100.0+REAL(J)
 200    CONTINUE          
 100  CONTINUE    
      DO 300 I=1,10
        T2(I)=REAL(I)*1.1
 300  CONTINUE     
      CALL MYSUB(10,15,MYARR,T2)
      END PROGRAM

      SUBROUTINE MYSUB(N,M,RARR,T)
C     PARAMTERS:
C          N
C          M
C          ARR
      IMPLICIT NONE
      INTEGER N,M
      REAL RARR(10,*)
      REAL T(*)
      INTEGER I, J
      WRITE (*,200), (T(I),I=1,10)      
      DO 100 I=1,10
          WRITE (*, 300), (RARR(I,J),J=1,15)
 100  CONTINUE    
 200  FORMAT(5F5.1/);
 300  FORMAT(15F6.0);
      END
