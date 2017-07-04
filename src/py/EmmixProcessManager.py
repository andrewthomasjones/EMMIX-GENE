# (c) Department of Mathematics,
#     University of Queensland
#     2002,2003
#
# $Revision: 1.4 $
# $Log: EmmixProcessManager.py,v $
# Revision 1.4  2002/12/29 05:53:48  default
# Lists stdout of running processes
#
#
"""Emmix Process Manager

Synopis:
    >>>thread.start_new_thread(EmmixProcessManager.spawn, ...)
    >>>EmmixProcessManager.listRunningProcesses()
    [ ('select-genes.py', 'foo.dat', 'temp/sgin.1234', 'temp/sgout.1234'),
      ('cluster-genes.exe', 'bar.dat.cut', ... )]
     
     
"""

import shelve
import win32process 
import win32file
import win32event
import os
import re

PROCESSMANAGER_FILENAME = "var/processes.db"
messages=[]

def listRunningProcesses():
    "Returns a list of (program_file, data_file, stdin_file, stdout_file)"
    d = shelve.open(PROCESSMANAGER_FILENAME)
    patt = re.compile("(.+)<(.+)>(.+)")
    
    list = []
    for pid in d.keys():
        commandline = d[pid]
        try:
            match=patt.match(commandline)
        except TypeError:
            pass # we are expecting a string
        else:            
            if match:
                command, stdin_file, stdout_file = match.groups()
                command, stdin_file, stdout_file = \
                    command.strip(), stdin_file.strip(), stdout_file.strip()
                command = command.replace("  "," ")
                exe, data, data2, data3 = command.split(" ",3,)
                if exe.upper().endswith("PYTHON.EXE"):
                    exe, data = data, data2
                list.append((exe,data,stdin_file,stdout_file))                
            else:
                print "WARNING: %s does not match pattern" % commandline
    d.close()

    return list
        
def isRunning(emmixrule, emmixdata):
    "Returns True if the current set of rule and data are being run"
    #
    # default=false
    #
    result = 0
    
    d = shelve.open(PROCESSMANAGER_FILENAME)
    key = __emmix_hash(emmixrule, emmixdata)
    if d.has_key(key):
        pid = d[key]
        if pid in __pids():
            result = 1 
        else:
            #
            # process terminated. get rid of the key
            #
            del d[key]
    d.close()
    return result

def update():
    """Updates the database, removing all processes
    which are no longer running"""
    running_pids = list()
    d = shelve.open(PROCESSMANAGER_FILENAME)
    for key in d.keys():
        if not key in running_pids:
            del d[key]
    d.close()

def list():
    """returns a list of currently running processes"""
    list = []
    d = shelve.open(PROCESSMANAGER_FILENAME)
    for key in d.keys():
        pid = d[key]
        if pid in __pids():
            list.append(__getProcessInfo(pid))
    d.close()
    return list
        
def listExes(matches=[]):
    # convert to upper case
    matches = map(lambda match: match.upper(), matches)
    exes = __exeNames()
    exes = map(os.path.basename, exes)
    exes = map(lambda exe: exe.upper(), exes)
    list = []
    for exe in exes:
        for match in matches:
            if exe[:10] == match[:10]:
                list.append(match)
    #exes = filter(lambda x, match=match: x in match, exes)
    #return exes
    return list

def spawnObsolete(emmixrule, emmixdata, cmdline):
    """starts up a process, and automatically registers
    the process using notifyRunning.
    
    Example:
        launch(rule, data, 'foo.exe < bar1 > bar2')"""
    #
    # work out the stdin and stdout
    #
    filein=''
    fileout=''
    #
    # create a batch file in the 
    # current directory
    #
    app = cmdline.split()[0]
    bat = os.path.splitext(app)[0] + '.bat'
    open(bat,'w').write(cmdline)
    if ">" in cmdline:
        split = cmdline[cmdline.rindex(">")+1:].split()
        fileout = split[0]
        cmdline = cmdline[:cmdline.rindex(">")] + \
          " ".join(split[1:])

    if "<" in cmdline:
        split = cmdline[cmdline.index("<")+1:].split()
        filein = split[0]
        cmdline = cmdline[:cmdline.rindex("<")] + \
          " ".join(split[1:])          
    
    app = cmdline.split()[0]
    pid, hProcess = _CreateProcess(app, cmdline.split()[1:], filein)
    notifyRunning(emmixrule, emmixdata, pid, cmdline)
    #
    # block
    waitUntilStopped(hProcess)

def spawn(emmixrule, emmixdata, cmdline):
    """Use win32pipe instead of CreateProcess"""
    pid=9999
    notifyRunning(emmixrule, emmixdata, pid, cmdline)
    #
    # create a batch file in the 
    # current directory
    #
    app = cmdline.split()[0]
    if app.lower().find("python.exe") >= 0:
        app = cmdline.split()[1]
    bat = os.path.splitext(app)[0] + '.bat'
    open(bat,'w').write(cmdline)
    #
    #r=win32pipe.popen(cmdline,'w')
    child_stdin,child_stdout,child_stderr = os.popen3(cmdline,'t')
    while 1:
        line=child_stderr.readline()
        #line=child_stdout.readline()
        if not line: break
        print line[:-1]
        if line.find("ERROR")>=0:
            messages.append("%s: %s" % (app,line[:-1]))
    notifyStopped(emmixrule, emmixdata)

def notifyRunning(emmixrule, emmixdata, pid, commandline=""):
    "Note that the current process is running"
    key = __emmix_hash(emmixrule, emmixdata)
    d = shelve.open(PROCESSMANAGER_FILENAME)
    #d[key]=pid
    d[key]=commandline
    d.close()

def notifyStopped(emmixrule, emmixdata):
    "Note that the given process has stopped"
    key = __emmix_hash(emmixrule, emmixdata)
    d = shelve.open(PROCESSMANAGER_FILENAME)
    if d.has_key(key): del d[key]
    d.close()

def waitUntilStopped(hProcess):
    "Blocks untils the process has terminated"
    win32event.WaitForSingleObject(hProcess, win32event.INFINITE)

#--------------------------------------------------------------------------
# Private functions
#--------------------------------------------------------------------------

#def __getProcessInfo(pid):
#    "Returns all available information for a given process id"
#    try:
#        return __getProcessInfo_toolhelp(pid)
#    except:
#        return __getProcessInfo_pdh(pid)

def __getProcessInfo_toolhelp(pid):
    """Returns all available information for a given process id
    using the toolhelp API"""
    h = tlhelp32.CreateToolhelp32Snapshot(tlhelp32.TH32CS_SNAPPROCESS, 0)
    if h:
        pe = tlhelp32.PROCESSENTRY32()
        pe.dwSize=296
        try:
            b = tlhelp32.Process32First(h, pe)
            while b:
                list.append(pe.th32ProcessID)
                b = tlhelp32.Process32Next(h, pe)
        finally:
            tlhelp32.CloseHandle(h)
    return list
    
def __getProcessInfo_pdh(pid):
    pass

#def __pids():
#    "Returns a list of currently running pids"
#
#    try:
#        return __pids_toolhelp()
#    except:
#        return __pids_pdh()

def __pids_toolhelp():
    """Returns a list of currently running pids using the
    toolhelp API"""
    list = []
    h = tlhelp32.CreateToolhelp32Snapshot(tlhelp32.TH32CS_SNAPPROCESS, 0)
    if h:
        pe = tlhelp32.PROCESSENTRY32()
        pe.dwSize=296
        try:
            b = tlhelp32.Process32First(h, pe)
            while b:
                list.append(pe.th32ProcessID)
                b = tlhelp32.Process32Next(h, pe)
        finally:
            tlhelp32.CloseHandle(h)
    return list
            
#def __exeNames():
#    "Returns a list of exe names of currently running processes"
#    try:
#        return __exeNames_pdh()
#    except:
#        return __exeNames_toolhelp()
    
def __exeNames_toolhelp():
    """Returns a list of exe names of currently running processes
    with the toolhelp API"""
    list = []
    import tlhelp32
    h = tlhelp32.CreateToolhelp32Snapshot(tlhelp32.TH32CS_SNAPPROCESS, 0)
    if h:
        pe = tlhelp32.PROCESSENTRY32()
        pe.dwSize=296
        try:
            b = tlhelp32.Process32First(h, pe)
            while b:
                list.append(pe.szExeFile)
                b = tlhelp32.Process32Next(h, pe)
        finally:
            tlhelp32.CloseHandle(h)
    return list

def __exeNames_pdh():
    return []

def __pids_pdh():
    return []
    raise "Unimplemented"

try:
	import tlhelp32
	__getProcessInfo = __getProcessInfo_toolhelp
	__pids = __pids_toolhelp
	__exeNames = __exeNames_toolhelp
except:
	__getProcessInfo = __getProcessInfo_pdh
	__pids = __pids_pdh
	__exeNames = __exeNames_pdh
	

def __emmix_hash(emmixrule, emmixdata):
    if hasattr(emmixrule, '__dict__') and \
        hasattr(emmixdata, '__dict__'):
        return str(hash(`emmixrule.__dict__` + `emmixdata.__dict__`))
    else:
        return 'abcdef' 

def _CreateProcess(app, args, filein):

    """Returns the pid.
       app = executable name
       args = list of arguments
       filein = name of file to redirect to stdin
    """
 
    SI = win32process.STARTUPINFO()
    SI.dwFlags = win32process.STARTF_USESTDHANDLES
    SI.hStdInput = win32file.CreateFile(
        filein,                 # 
        win32file.GENERIC_READ, #
        0,                      #
        None,                   #
        win32file.OPEN_ALWAYS,  #
        0,                      #
        0                       #
    )

    SI.hStdOutput = win32file.CreateFile(
        "debugoutput.txt",
         win32file.GENERIC_WRITE,
         0,
         None,
         win32file.CREATE_ALWAYS,
         0,
         0
    )

    cmdline = app + " " + " ".join(args)
    hProcess, hThread, pid, threadid =  win32process.CreateProcess( \
        app, cmdline, None,     #
        None,                   #
        1,                      # Inherit handles
        win32process.DETACHED_PROCESS,  #
        None, None, SI)

    return pid, hProcess

if __name__=="__main__":
    spawn(None, None, "..\\bin\\python.exe foo bar < baz > baz2")    
