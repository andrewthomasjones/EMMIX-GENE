
#import EmmixProcessManager
#
#EmmixProcessManager.spawn(None, None, "epmtest.exe popen3 < epmtestin2.txt")

import os
cmd = "epmtest.exe popen3 < epmtestin2.txt > emptestout2.txt"
cmd = "epmtest.exe popen3 < epmtestin2.txt > emptestout2.txt"

# This is ok
cmd = "C:\\python21\\python.exe epmtest.py popen3 < epmtestin2.txt > emptestout2.txt"

# Don't do this --> will fill up stdout buffer
#cmd = "C:\\python21\\python.exe epmtest.py popen3 < epmtestin2.txt" 

# Try piping in stdin, not ok
#cmd = "C:\\python21\\python.exe epmtest.py popen3 > epmtestout2.txt" 

stdin,stdout,stderr=os.popen3(cmd, "t")
#lines=open("epmtestin2.txt","r").readlines()
#for line in lines:
#    stdin.write(line)
counter = 0
while 1:
    #stdin.write(lines[counter] + "\n")
    #stdin.flush()
    line = stderr.readline()    
    if not line:
        break
    print line
    counter +=1
stdin.close()
stdout.close()
stderr.close()
