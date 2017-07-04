# emmixgene/webutil.py
# change history:
# $Log: webutil.py,v $
# Revision 1.8  2003/06/27 16:27:38  chui.tey
# Added more exclusions for file list
#
# Revision 1.7  2002/12/27 16:29:00  default
# Tidied up file selection more
#
# Revision 1.6  2002/12/27 16:10:53  default
# File selection screen with improved look and feel
#
# Revision 1.5  2002/12/27 15:20:00  default
# Optimize file selection
#
# Revision 1.4  2002/12/26 23:44:46  default
# z2.py
#
#
"""
 Provide utility libraries for web applications
"""
import os
import time

standard_html_header = ""
standard_html_footer = ""

def select_path(REQUEST, caption="", filter=None, file=None, src="/", initial_file=""):
    """Lists all the files in directories and subdirectories"""
    #
    # check if result has been returned
    #
    if file: 
        #
        # Yes, redirect back to the originating caller
        #
        url="%s?file=%s" % (src, file)
        REQUEST.response.redirect(url)
        return

    #
    # Populate 'filenames' with list of filenames
    # which has the word .dat inside
    # 

    # output to file, faster than using popen
    os.system("dir /s/b > dir.tmp")
    files = []
    curdir = os.getcwd()
    splitext = os.path.splitext
    basename = os.path.basename
    for filename in open("dir.tmp","r").readlines():
        filename = filename[:-1]    # like 'chomp'
        ufilename = filename.upper()
        base = basename(ufilename)
        if base.find('.DAT') >= 0:
            ext = splitext(base)[1]
            if ext not in ('.SSTATS', '.STATS','.PNG', '.TMP', '.SVG', '.EMD') \
               and not ext.endswith("~"):
                if ufilename.find(".CUT.EMMIXT") == -1:
                    if os.path.getsize(filename) > 0:
                        files.append(filename)
    os.unlink("dir.tmp")
    
    # Optimization: Check for unins000.dat once only
    try:
        files.remove(os.path.join(curdir,'unins000.dat'))
    except:
        pass

    # Optimization. Don't write long strings. Compute len(curdir) once only
    files_html=[]
    len_curdir=len(curdir)+1
    for file in files:
        directory,base = os.path.split(file)
        relpath = file[len_curdir:]
        files_html.append( \
        """
        <tr>
            <td>%(directory)s</td>
            <td>
            <a href="/webutil/select_path?src=%(src)s&file=%(relpath)s">
            %(base)s
            </td>
        </tr>
        """  % locals())
    body = files_html = "".join(files_html)

    # note: review.htm uses 'body','caption','parent'
    parent = '/main_' + caption
    caption = caption.title().replace("_"," ")
    return apply_template('select_file.htm', locals(), globals())
    
    # Local variables for populating templates
    html_header = standard_html_header
    html_footer = standard_html_footer
    datadir     = os.getcwd() + "\\data"
    return """
    %(html_header)s
    <h2>Specify a file from the list below</h2> 
    <p>(Your current choice is %(initial_file)s)<p/>
    <p>%(caption)s</p>

    <table border="0">
      <tr><td>Directory</td><td>Filename</td></tr>
      %(files_html)s 
    </table>

    <div align="right">
        <form action="/" method="post">
        <input type="submit" value="Cancel"/>
        </form>
    </div>

    <p>By default all data files are held in the data directory
       (ie. %(datadir)s).
       If you would like to import files, click
       <a href="file://%(datadir)s" target="_blank">here</a> to open
       the data directory. You can then use drag and drop
       to copy files into this directory.
    </p>
    
    %(html_footer)s""" % locals()
        
def select_directory(REQUEST, dir=None, rootdir=None, src=None):
    "Allows user to select a directory"
    if dir:
        REQUEST.response.redirect("%s?dir=%s" % (src, dir))
        return

    option_formatted="Select output directory"
    img_select_genes="dummy"
    img_cluster_genes="dummy"
    img_cluster_tissues="dummy"

    directories = recurse_dir(rootdir,src)
    menus = """
    <b>Select one of the folders below to output the results to</b>
    %(directories)s
    <h2>or specify a new folder</h2>
    <form method="post">
        <input type="hidden" name="rootdir" value="%(rootdir)s">
        New folder name
        <input type="text" name="createfolder" value="results\\&lt;your folder name here&gt;" size="30">
        <input type="submit" value="OK">
    </form>""" % locals() 
    return apply_template('menu_template.htm', locals(), {})

def recurse_dir(root, src):

    html='<img src="images/folder.gif" border="0"><a href="/webutil/select_directory?dir=%s&src=%s">%s</a><br/>\n' % (root, src, root)
    for dir in os.listdir(root):
        fullpath=os.path.join(root,dir)
        if os.path.isdir(fullpath):
            html += '%s' % recurse_dir(fullpath, src)
           
    return html

class FileSystemDirectory:
    "File System Object"

    def __init__(self, dir):
        self.dir = dir

    def __getattr__(self, attr):
        "Returns the file given by attr"

        filename = os.path.join(self.dir, attr)
        mime_type = self._getMimeType(filename)

        def curry(self, mime_type=mime_type, filename=filename, REQUEST=None):
            if REQUEST and REQUEST.get('HTTP_IF_MODIFIED_SINCE',None):
                REQUEST.response.setStatus(304) # Not Modified
                return
            else:
                contents = open(filename,'rb').read()
                expire_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", \
                    time.gmtime(time.time() + 24 *3600.0))
                REQUEST.response.setHeader("Expires", expire_time) 
                REQUEST.response.setHeader("Content-Type", mime_type)
                REQUEST.response.setHeader("Content-Length", len(contents))
                return contents

        curry.__doc__ = "Reads file"
                
        if os.path.isfile(filename):
            # if os.path.splitext(filename)[1]=='.gif':
            return curry

        raise AttributeError
        
    def _getMimeType(self, filename):
        extension = os.path.splitext(filename)[1].lower()
        if extension == '.gif':
            return 'image/gif'
        elif extension == '.jpg' or extension == '.jpeg':
            return 'image/jpeg'
        elif extension == '.png':
            return 'image/png'
        elif extension == '.css':
            return 'text/css'
        else:
            return 'application/octet-stream'

#-----------------------------------------------------------------------
# utility functions 
#-----------------------------------------------------------------------

def apply_template(filename, dict_locals, dict_globals):
    dummy = 'dFmaHg'
    template = open( 'template\\' + filename, 'r').read()
    template = template.replace( '%"', dummy )
    result = template % _multimap( dict_locals, dict_globals )
    result = result.replace( dummy, '%"')
    return result

def _multimap(arg1, *args):
    dict = arg1
    for arg in args:
        dict.update(arg)
    return dict


