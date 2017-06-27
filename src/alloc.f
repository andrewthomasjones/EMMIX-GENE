        subroutine allocs(n,p)
        implicit none
        integer n,p,i,j
        real vector (n,p)
        real matri2 (n,p,p)
        do i=n-3,n
            do J=p-3,p
                vector(i,j) =i*100+j
                matri2(i,j,j)=i*100+j
            end do
        end do
        DO i=n-3,n
          print *, (vector(i,j),J=p-3,p)
        END DO     
        call sub2(vector,n,p)
        end

        subroutine sub2(vector,n,p)
        implicit none
        integer n,p,i,j
        real vector(n,p)
        print *, 'From Sub2()'
        DO i=n-3,n
          print *, (vector(i,j),J=p-3,p)
        END DO     
        end
        
        program testalloca
        implicit none
        integer n,p
        print *, 'Array dimension?'
        read *, n
        print *, 'Array dimension?'
        read *, p
        call allocs (n,p)
        end
