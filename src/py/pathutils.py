# (c) Department of Mathematics,
#     University of Queensland
#     2002
#
# $Log: pathutils.py,v $
# Revision 1.5  2002/12/29 05:56:20  default
# Bug fix
#
# Revision 1.4  2002/12/27 10:11:43  default
# Bug fixes
#
# Revision 1.3  2002/12/27 09:50:10  default
# Fixed bug in safecopy
#
# Revision 1.2  2002/12/27 09:47:01  default
# Use recurse_mkdir, copies stdout to result directories
#
# Revision 1.1  2002/12/27 08:47:48  default
#

import os
import shutil

def safecopy(src, dst):
    """
    Copies a file from src to destination
    provided the src and destination are different
    and src file exists. 
    If destination paths don't exist then creates them.
    """
    abs_src = os.path.abspath(src)
    abs_dst = os.path.abspath(dst)
    if (abs_src != abs_dst) \
        and os.path.isfile(abs_src):            
        dirname = os.path.dirname(abs_dst)
        recurse_mkdir(dirname)
        shutil.copy(abs_src, abs_dst)
    
def relative_path(base, target):
  """Given two absolute pathnames base and target,
  returns a relative pathname to target from the
  directory specified by base. If there is no common
  prefix, returns the target path unchanged.
  """
  common, base_tail, target_tail = split_common(base, target)
  #print "common:", common
  #print "base_tail:", base_tail
  #print "target_tail:", target_tail
  r = len(base_tail) * [os.pardir] + target_tail
  if r:
    return os.path.join(*r)
  else:
    return os.curdir

def split_common(path1, path2):
  """Return a tuple of three lists of pathname components:
  the common directory prefix of path1 and path2, the remaining
  part of path1, and the remaining part of path2.
  """
  p1 = split_all(path1)
  p2 = split_all(path2)
  c = []
  i = 0
  imax = min(len(p1), len(p2))
  while i < imax:
    if os.path.normcase(p1[i]) == os.path.normcase(p2[i]):
      c.append(p1[i])
    else:
      break
    i = i + 1
  return c, p1[i:], p2[i:]

def split_all(path):
  """Return a list of the pathname components of the given path.
  """
  result = []
  head = path
  while head:
    head2, tail = os.path.split(head)
    if head2 == head:
      break # reached root on Unix or drive specification on Windows
    head = head2
    result.insert(0, tail)
  if head:
    result.insert(0, head)
  return result

def recurse_mkdir(path):
    """
    Recursively make directories
    """
    drive,path_nodrive=os.path.splitdrive(path)
    dirs = path_nodrive.split(os.sep)
    try:
        for i in range(len(dirs)):
            dir = os.path.join(*dirs[:i+1])
            if dir and not os.path.isdir(dir):
                os.mkdir(dir)
    except os.error:
        print "os.mkdir failed at '%s' for '%s'" % (dir,path)


