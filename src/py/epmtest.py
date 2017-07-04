def test_popen3():

    import sys

    counter = 0

    print >> sys.stderr, "Testing popen3"
    sys.stderr.flush()
    sys.stdout.flush()
    sys.stdin.flush()

    while 1:
        line = sys.stdin.readline()[:-1]
        if not line:
            break
        print >> sys.stdout, line
        print >> sys.stderr, "ANNOUNCE: count #%5d" % counter
        #sys.stderr.flush()
        counter += 1
        
    print >> sys.stderr, "ANNOUNCE: EOF encountered"
    sys.stderr.flush()

    sys.stderr.close()
    sys.stdout.close()
    sys.stdin.close()

test_popen3()
