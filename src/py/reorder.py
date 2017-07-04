#
# Department of Mathematics
# University of Queensland
# (c) Copyright 2002 
# All Rights Reserved
#
# Developer: Chui Tey
#
# reorder.py
#
# $Log: reorder.py,v $
# Revision 1.1  2002/07/17 10:33:19  default
# Initial check-in
#
#
from pprint import pprint

def reorder_columns(matrix_filename, sort_filename):    
    #
    # read the sort order
    sort_order = map(lambda x: int(x), open(sort_filename, "r").read().split() )

    #
    # read the matrix
    #
    matrix = []
    for line in open(matrix_filename, 'r').readlines():
        columns = map(lambda x: float(x), line.split() )
        matrix.append(columns)

    return _reorder_columns(matrix, sort_order)
    
def _reorder_columns(matrix, sort_order):

    # 1. invert, 
    # 2. form a tuple with sort order
    #    eg. [(1, [#1, #2, ...]), ...
    # 3. sort on the sort order
    # 4. remove sort order
    # 5. invert back to original again
    #
    matrix = transpose(matrix)
    new_matrix = []
    for sort_value, row in zip(sort_order,matrix):
        new_matrix.append((sort_value, row))
    new_matrix.sort()
    matrix =[row for (sort_value, row) in new_matrix]
    matrix = transpose(matrix)
    return matrix

def transpose(matrix):
    rows=len(matrix)
    cols=len(matrix[0])
    new_matrix = [[] for x in range(cols)] 
    for row in matrix:
        for col,colnumber in zip(row, range(len(row))):
            new_matrix[colnumber].append(col)
    return new_matrix

def print_matrix(matrix):
    import sys
    for row in matrix:
       for column in row:
          #sys.stdout.write("%8.5f " % column)
          sys.stdout.write("%f " % column)
       print 

def test1():
    matrix = [ [1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]]
    print_matrix(matrix)
    print_matrix(transpose(matrix))
    
def test2():
    matrix = reorder_columns('results/2000/alon_norm.dat.cut_groupmeans','results/2000/cluster-tissues.txt')
    print_matrix(matrix)
    
def test3():
    matrix = [ [1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]]
    sort_order = [4,3,2,1]               
    print_matrix(matrix)
    print_matrix(_reorder_columns(matrix, sort_order))

if __name__ == '__main__':
    #test2() 
    #test3() 
    import sys
    matrix_filename = sys.argv[1]
    reorder_filename = sys.argv[2]
    matrix = reorder_columns(matrix_filename, reorder_filename)
    print_matrix(matrix)

