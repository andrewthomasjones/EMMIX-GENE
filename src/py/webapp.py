# (c) Department of Mathematics,
#     University of Queensland
#     2002
#
# $Log: webapp.py,v $
# Revision 1.20  2003/07/25 15:52:54  chui.tey
# Read formatted .sstats file
#
# Revision 1.19  2003/07/08 06:28:48  chui.tey
# Use original data file for the number of genes
#
# Revision 1.18  2003/06/27 17:17:05  chui.tey
# select data files, preserve the context using cookies
#
# Revision 1.17  2003/06/27 16:31:39  chui.tey
# Review list file with gene descriptions
#
# Revision 1.16  2003/06/27 15:27:14  chui.tey
# Review sstats
#
# Revision 1.16  2003/01/01 04:20:42  Administrator
# Removed unnecessary assert statement
#
# Revision 1.15  2002/12/29 05:51:29  default
# Displays stdout of running processes
#
# Revision 1.14  2002/12/27 16:29:01  default
# Tidied up file selection more
#
# Revision 1.13  2002/12/27 09:47:01  default
# Use recurse_mkdir, copies stdout to result directories
#
# Revision 1.12  2002/12/26 23:44:46  default
# z2.py
#
# Revision 1.11  2002/09/22 05:35:32  default
# Added creation of SVG heatmaps
# Added templating to viewing sstats, stats result files
#
# Revision 1.10  2002/09/15 09:45:59  default
# Thumbnails now uses templates
# Review sstats and stats files reads gene description
#
# Revision 1.9  2002/07/08 13:04:21  default
# Use templates for program configuration
#
# Revision 1.8  2002/07/03 13:12:31  default
# Refactored apply_templates to webutil
# Refactored calcCorrelation to emmixgene
# Conditionally display link to show_correlation_heatmaps
#
# Revision 1.7  2002/06/29 11:04:17  default
# Added docoeff.exe. Refactored review_thumbnails.
#
# Revision 1.6  2002/06/25 16:25:02  default
# now use templates
# refactored _up_to_date function
# initial stubs for docoeff.exe
#
# Revision 1.5  2002/05/04 02:15:06  default
# Carefully copy data files into result directory
# Cleaned up what files to display in review/...
#
# Revision 1.4  2002/04/11 12:36:29  default
# Bug fix: Cannot review other result directories
#
# Revision 1.3  2002/04/10 20:44:46  default
# Added resume capability to select-genes
# Added report back capability
#
# Revision 1.2  2002/04/03 09:59:57  default
# Self repairing configuration directories
# Configuration directory in ./configuration, more obvious
# Pre-checks data files exists before running
# Refactored initialization code
#
#
"webapp module"

#import DocumentTemplate
import heatmap
import heatmapsvg
import os
import sys
import shutil
import emmixgene
import time
import locale
import webutil
import MessageStore
import EmmixProcessManager
from pathutils import recurse_mkdir

def initialize():

    global program
    global here
    global RESULT_PATH
    global CURRENT_RULE_DIR
    global CURRENT_RULE_PATH
    global CURRENT_DATA_PATH
    global CURRENT_DATAFILES_PATH
    global CURRENT_OUTPUTDIR_PATH
    global current_rule
    global current_datafiles
    global current_outputdir

    program = sys.argv[0]
    here = os.path.join(os.getcwd(), os.path.split(program)[0])

    RESULT_PATH=os.path.join(here,'results')

    CURRENT_RULE_DIR=os.path.join(here,'configuration')
    CURRENT_RULE_PATH=os.path.join(CURRENT_RULE_DIR,'rule')
    CURRENT_DATA_PATH=os.path.join(here,'data')
    CURRENT_DATAFILES_PATH=os.path.join(CURRENT_RULE_DIR,'datafiles')
    CURRENT_OUTPUTDIR_PATH=os.path.join(CURRENT_RULE_DIR,'outputdir')

    if not os.path.isdir(CURRENT_RULE_DIR):
        recurse_mkdir(CURRENT_RULE_DIR)

    current_rule=emmixgene.EmmixRule()
    current_datafiles=emmixgene.EmmixDataFiles('data\\alon_norm.dat')
    current_outputdir="results\\001"

    if os.path.isfile(CURRENT_RULE_PATH):
        current_rule.restore_rule(CURRENT_RULE_PATH)
    else:
        current_rule.store_rule(CURRENT_RULE_PATH)

    if os.path.isfile(CURRENT_DATAFILES_PATH):
        current_datafiles.restore(CURRENT_DATAFILES_PATH)
    else:
        current_datafiles.store(CURRENT_DATAFILES_PATH)

    if os.path.isfile(CURRENT_OUTPUTDIR_PATH):
        current_outputdir=open(CURRENT_OUTPUTDIR_PATH).read()
    else:
        open(CURRENT_OUTPUTDIR_PATH,"w").write(current_outputdir)

    # Set to default locale
    locale.setlocale(locale.LC_ALL,"")

initialize()

#-----------------------------------------------------------------------
# /index_html
#-----------------------------------------------------------------------

def index_html(REQUEST, RESPONSE):
    "Obligatory doc_string"

    msgs.restore('messages.txt')
    messages=msgs.displayMessages()

    select_genes_filename=current_datafiles.select_genes.filename
    cluster_genes_filename=current_datafiles.cluster_genes.filename
    cluster_tissues_filename=current_datafiles.cluster_tissues.filename
   
    RESPONSE.setHeader("Expires","-1")
    RESPONSE.setHeader("Cache-Control", "no-cache")
    RESPONSE.setHeader("Pragma", "no-cache")

    if messages:
        messages="""
<h3>Messages</h3>
<table bgcolor="#cccc99" border="0">
  <tr>
    <td>
     %(messages)s   
    </td>
  </tr>
  <tr align="right">
    <td>
      <a href="/msgs/deleteAllMessages">Delete all messages</a>
    </td>
  </tr>
</table>
""" % locals()

    return webutil.apply_template('default.htm', locals(), globals())

    html ="""
%(standard_html_header)s

<H2>Main menu</H2>

<table valign="top">
<tr valign="top">
<td valign="top">

<p>
  <a href="/main_select_genes">Select-genes</a>
</p>

<p>
  <a href="/main_cluster_genes">Cluster-genes</a>
</p>

<p>
  <a href="/main_cluster_tissues">Cluster-tissues</a>
</p>

</td>
<td>

<h3>Running processes</h3>
<table bgcolor="#cccc99" border="0">
  <tr>
    <td>
     %(runningProcesses)s   
    </td>
  </tr>
</table>  

<!-- **************** MESSAGES ************* -->
%(messages)s

<p>
<a href="/reportBack">Create an error report</a> for Chui</a>
</p>

</td>
</tr>
</table>

<hr/>

<H2>Help</H2>

<p><b>select-genes</b> uses the emmix algorithm to reduce a large dataset
of genes to a smaller set which is subsequently used for clustering.</p>

<p><b>cluster-genes</b> clusters commonly expressed genes into groups.</p>

<p><b>cluster-tissues</b> ... </p>

%(standard_html_footer)s
""" % _multimap(locals(), globals())
    return html % _multimap(locals(), globals())

#-----------------------------------------------------------------------
# /common_main_menu
#-----------------------------------------------------------------------
def main_common( filename,option='select_genes' ):
    global current_outputdir
    cod = current_outputdir
    img_select_genes = 'dumy'     # required for menu_template.htm
    img_cluster_genes = 'dummy'   # required for menu_template.htm
    img_cluster_tissues = 'dummy' # required for menu_template.htm
    if option=='select_genes': img_select_genes = 'img' 
    if option=='cluster_genes': img_cluster_genes = 'img' 
    if option=='cluster_tissues': img_cluster_tissues = 'img' 
    if option=='select_genes':
        program = 'all'
    else:
        program = option
    option_formatted = option.replace("_"," ").title()
    menus = \
    """
    <font size="2" face="Arial">
    <p> <a href="conf_select_data?program=%(program)s&filter=*.dat&initial_file=%(filename)s">Specify</a> data file. (Currently %(filename)s)</p>
    <p> <a href="conf_select_genes">Set options for %(option_formatted)s</a></p>
    <p> <a href="conf_select_outputdir">Specify output directory</a>. 
         (Currently %(cod)s )
    </p>
    <p> 
         <form method="post" action="/run">
         <input type="hidden" name="select_genes" value="1" />
         <input type="submit" value="GO"/>
         </form>
    </p>
    <p> <a href="/review">Review</a> results</p>
    </font>
""" % locals()
    menus = menus.replace('select_genes', option)
    return webutil.apply_template('menu_template.htm', locals(), globals())

#-----------------------------------------------------------------------
# /main_select_genes
#-----------------------------------------------------------------------
def main_select_genes():
    """Main menu for select genes subprogram"""
    filename=current_datafiles.select_genes.filename
    return main_common(filename, 'select_genes')

#-----------------------------------------------------------------------
# /main_cluster_genes
#-----------------------------------------------------------------------
def main_cluster_genes():
    """Main menu for cluster genes subprogram"""
    filename=current_datafiles.cluster_genes.filename
    return main_common(filename, 'cluster_genes')


#-----------------------------------------------------------------------
# /main_cluster_tissues
#-----------------------------------------------------------------------
def main_cluster_tissues():
    """Main menu for cluster tissues subprogram"""
    filename=current_datafiles.cluster_tissues.filename
    return main_common(filename, 'cluster_tissues')

#-----------------------------------------------------------------------
# /conf_select_genes
#-----------------------------------------------------------------------
def conf_select_genes(REQUEST):
    """Screen to configure select genes parameters"""

    global current_rule

    if REQUEST['REQUEST_METHOD']=="POST":
        #
        # By default limit the number of rows
        # unless specified
        #
        limit_rows=1
        if REQUEST.has_key('limit_rows'):
            if REQUEST['limit_rows']=='0':
                limit_rows=0
        for key in current_rule.params_select_genes.keys():
            if REQUEST.has_key(key):
                if key == 'num_rows' and not limit_rows:
                    current_rule.params_select_genes['num_rows']=0
                elif REQUEST[key]:
                    current_rule.params_select_genes[key]=REQUEST[key]
        for key in ['resume']:
            if not REQUEST.has_key(key):
                current_rule.params_select_genes[key]=0
        current_rule.store_rule(CURRENT_RULE_PATH)
        REQUEST.response.redirect("/main_select_genes")
        return ""

    option_formatted = """
    <a href="/main_select_genes">Select Genes</a> &gt; Options
    """
    img_select_genes = "img"
    img_cluster_genes = "dummy"
    img_cluster_tissues = "dummy"

    html = """

<h2>Options to run select-genes with</h2>

<form action="" method="post">

<table>
  <tr>
  <td>Random starts</td>
  <td><input type="text" name="random_starts" value="%(random_starts)s"></td>
  </tr>

  <tr>
  <td>K-Mean starts</td>
  <td><input type="text" name="kmean_starts"  value="%(kmean_starts)s"></td>
  </tr>

  <tr>
  <td>Random seed 1</td>
  <td><input type="text" name="random_seed1"  value="%(random_seed1)s"></td>
  </tr>

  <tr>
  <td>Random seed 2</td>
  <td><input type="text" name="random_seed2"  value="%(random_seed2)s"></td>
  </tr>
  
  <tr>
  <td>Random seed 3</td>
  <td><input type="text" name="random_seed3"  value="%(random_seed3)s"></td>
  </tr>

  <tr>
  <td>Threshold likelihood</td>
  <td><input type="text" name="threshold_likelihood" 
 value="%(threshold_likelihood)s"></td>
  </tr>
  
  <tr>
  <td>Threshold cluster size</td>
  <td><input type="text" name="threshold_clustersize"
 value="%(threshold_clustersize)s"></td>
  </tr>

<!-- ============== limit number of rows computed ============== -->
  <tr>
  <td colspan="2">
  <input type="radio" id="limit_rows" name="limit_rows" value="1">Limit rows
  <input type="radio" id="all_rows" name="limit_rows" value="0"/>
  Use all rows
  </td>
  </tr>
  
  <tr>
  <td>Number of rows to use (from top of file)</td> 
  <td><input type="text" name="num_rows" value="%(num_rows)s"></td>
  </tr>

<!-- ============= resume past calculation ===================== -->
  <tr>
  <td colspan="2">
  <input type="checkbox" 
         name="resume:int" 
         value="1" 
         checked="%(resume)s">If unfinished job exists, resume unfinished job.
  </td>
  </tr>

  <tr colspan="2">
  <td><input type="button" value="Restore to default"></td>
  </tr>

  <tr colspan="2">
  <td>
    <input type="submit" value="OK">
    <input type="submit" value="Cancel">
  </td>
  </tr>

</table>
""" % current_rule.params_select_genes 
    if current_rule.params_select_genes['num_rows']:
        html = html.replace('id="limit_rows"','checked')
    else:
        html = html.replace('id="all_rows"','checked')
    html = html.replace('checked="0"', '')
    menus = html
    return webutil.apply_template('menu_template.htm',locals(), globals()) 

#-----------------------------------------------------------------------
# /conf_cluster_genes
#-----------------------------------------------------------------------
def conf_cluster_genes(REQUEST):
    """Web screen to configure Cluster Genes parameters"""
    if REQUEST['REQUEST_METHOD']=="POST":
        #
        # By default limit the number of rows
        # unless specified
        #
        limit_rows=1
        if REQUEST.has_key('limit_rows'):
            if REQUEST['limit_rows']=='0':
                limit_rows=0
        for key in current_rule.params_cluster_genes.keys():
            if REQUEST.has_key(key):
                if key == 'num_rows' and not limit_rows:
                    current_rule.params_cluster_genes['num_rows']=0
                elif REQUEST[key]:
                    current_rule.params_cluster_genes[key]=REQUEST[key]
        for key in ['robust', 'reorder']:
            if not REQUEST.has_key(key):
                current_rule.params_cluster_genes[key]="no"
        current_rule.store_rule(CURRENT_RULE_PATH)
        REQUEST.response.redirect("/main_cluster_genes")
        return ""

    option_formatted = """
    <a href="/main_cluster_genes">Cluster Genes</a> &gt; Configure
    """
    img_select_genes = "dummy"
    img_cluster_genes = "img"
    img_cluster_tissues = "dummy"
    html = """

<h2>Options to run cluster-genes with</h2>

<form action="" method="post">

Random starts <input type="text" name="random_starts"
  value="%(random_starts)s"><br/>
K-Mean starts <input type="text" name="kmean_starts"
  value="%(kmean_starts)s"><br/>
Random starts spherical <input type="text" name="random_starts_spherical"
  value="%(random_starts_spherical)s"><br/>
K-Mean starts spherical <input type="text" name="kmean_starts_spherical"
  value="%(kmean_starts_spherical)s"><br/>
Number of groups to cluster <input type="text" name="cluster_groups"
  value="%(cluster_groups)s"><br/>
Threshold cluster size <input type="text" name="threshold_clustersize"
  value="%(threshold_clustersize)s"><br/>
Random seed 1 <input type="text" name="random_seed1"
  value="%(random_seed1)s"><br/>
Random seed 2 <input type="text" name="random_seed2"
  value="%(random_seed2)s"><br/>
Random seed 3 <input type="text" name="random_seed3"
  value="%(random_seed3)s"><br/>
Reorder tissues <input type="checkbox" name="reorder"
  id="reorder" value="yes" oldvalue="%(reorder)s"> <br/>
Robust <input type="checkbox" name="robust"
  id="robust"  value="yes" oldvalue="%(robust)s">  <br/>
Common value of nu <input type="text" name="nu"
  value="%(nu)s"> (robust version only) <br/>

<!-- ============== limit number of rows computed ============== -->
<input type="radio" id="limit_rows" name="limit_rows" value="1">Limit rows
<input type="radio" id="all_rows" name="limit_rows" value="0"/>
 Use all rows<br/>
Number of rows to use (from top of file) 
 <input type="text" name="num_rows" value="%(num_rows)s"><br/>

<input type="button" value="Restore to default"><BR/>
<input type="submit" value="OK">
<input type="submit" value="Cancel">
</p>

""" % current_rule.params_cluster_genes 
    if current_rule.params_cluster_genes['num_rows']:
        html = html.replace('id="limit_rows"','checked')
    else:
        html = html.replace('id="all_rows"','checked')
    #
    # replace checkboxes values
    #
    html = html.replace('oldvalue="yes"', 'checked')
    menus = html
    return webutil.apply_template('menu_template.htm',locals(), globals()) 

#-----------------------------------------------------------------------
# /conf_cluster_tissues
#-----------------------------------------------------------------------
def conf_cluster_tissues(REQUEST):
    """Screen to configure cluster tissue parameters"""
    if REQUEST['REQUEST_METHOD']=="POST":
        #
        # By default limit the number of rows
        # unless specified
        #
        limit_rows=1
        if REQUEST.has_key('limit_rows'):
            if REQUEST['limit_rows']=='0':
                limit_rows=0
        for key in current_rule.params_cluster_tissues.keys():
            if REQUEST.has_key(key):
                if key == 'num_rows' and not limit_rows:
                    current_rule.params_cluster_tissues['num_rows']=0
                elif REQUEST[key]:
                    current_rule.params_cluster_tissues[key]=REQUEST[key]
        current_rule.params_cluster_tissues['use_factor_analyzers']=\
            getattr(REQUEST, 'use_factor_analyzers', 0)
        current_rule.store_rule(CURRENT_RULE_PATH)
        REQUEST.response.redirect("/main_cluster_tissues")
        return ""

    option_formatted = """
        <a href="/main_cluster_tissues">Cluster Tissues</a> &gt; Options
    """
    img_select_genes = "dummy"
    img_cluster_genes = "dummy"
    img_cluster_tissues = "img"
    html = """

<h2>Options for cluster-tissues</h2>

<form action="" method="post">

Use factor analyzers 
 <input type="checkbox" 
        oldvalue="%(use_factor_analyzers)s"
        name="use_factor_analyzers" 
        value="1"/><br/>
Number of factors (only used with factor analyzers)
 <input type="text" 
        name="num_factors:int" 
        value="%(num_factors)s"><br/>
Number of components 
 <input type="text" 
        name="num_components:int"
        value="%(num_components)s"><br/>
Random starts 
 <input type="text" 
        name="random_starts:int"
        value="%(random_starts)s"><br/>
K-Mean starts
 <input type="text" 
        name="kmean_starts:int"
        value="%(kmean_starts)s"><br/>
Random seed 1
 <input type="text" 
        name="random_seed1:int"
        value="%(random_seed1)s"><br/>
Random seed 2
 <input type="text" 
        name="random_seed2:int"
        value="%(random_seed2)s"><br/>
Random seed 3
 <input type="text" 
        name="random_seed3:int"
        value="%(random_seed3)s"><br/>

<!-- ============== limit number of rows computed ============== -->
<input type="radio" id="limit_rows" name="limit_rows" value="1">Limit rows
<input type="radio" id="all_rows" name="limit_rows" value="0"/>
 Use all rows<br/>
Number of rows to use (from top of file) 
 <input type="text" name="num_rows" value="%(num_rows)s"><br/>

<p>
<input type="button" value="Restore to default"><BR/>
<input type="submit" value="OK">
<input type="submit" value="Cancel">
</p>

""" % current_rule.params_cluster_tissues 
    html = html.replace('oldvalue="1"', 'checked')
    if current_rule.params_cluster_tissues['num_rows']:
        html = html.replace('id="limit_rows"','checked')
    else:
        html = html.replace('id="all_rows"','checked')
    menus = html
    return webutil.apply_template('menu_template.htm',locals(), globals()) 

#-----------------------------------------------------------------------
# /display_info
#-----------------------------------------------------------------------

def display_info(stdout):
    "display the contents of a file given"
    filename = os.path.abspath(stdout)
    directory = os.path.split(filename)[0]
    if directory == os.path.join(os.getcwd(),"temp"):
        return open(filename,"r").read()
    else:
        raise "FileNotFound"

#-----------------------------------------------------------------------
# /edit_gene_info
#-----------------------------------------------------------------------
def edit_gene_info(datafile, result_dir, REQUEST):
    """ Presents the gene info in an editable format """

    global CURRENT_DATA_PATH

    # save gene_info
    if REQUEST.get('REQUEST_METHOD')=='POST':
        form = REQUEST.form
        keys = filter(lambda x: x.isdigit(), form.keys()) 
        keys = map(lambda x: int(x), keys)
        keys.sort()
        keys = map(lambda x: str(x), keys)
        genes_filename = os.path.join(CURRENT_DATA_PATH, datafile + ".genes")
        f=open(genes_filename, 'w')
        for key in keys:
            if key.isdigit():
                f.write(key + " " + form[key] + "\n")
        f.close()    
        
    results=emmixgene.EmmixResult( \
        CURRENT_DATA_PATH, \
        result_dir, \
        datafile)
    getGene=results.getGene
    gene_count = results.getGeneCount()

    result = []
    app = result.append
            
    app("<h1>Edit gene description</h1>")
    app("<style>body, td {font-family: Verdana; font-size:smaller;}</style>")
    if REQUEST.get('REQUEST_METHOD')=='POST':
        app("<b>Changes saved to %s</b><p>" % results.genes_filename)
    else:
        app("<b>Editing %s</b><p>" % results.genes_filename)
    app("<b><a link=top>menu</a></b>")
    app("<form method='post'>")
    app("<input type=hidden name='datafile' value='%s' />" % datafile)
    app("<input type=hidden name=result_dir value='%s' />" % result_dir)
    app("<ul>")
    app("<li><input type=submit value='Save changes' ></li>")
    app("<li><a href=#%d>Edit Gene # %d</a></li>" % (1,1))
    for idx in range(20, gene_count, 20):
        app("<li><a href=#%d>Edit Gene # %d</a></li>" % (idx, idx))
    app("</ul>")
    app("<table>")        
    for gene_num in range(1, gene_count+1):
        app("""<tr><td>%d</td><td><a name="%d">""" % (gene_num, gene_num))
        app("""<input name="%d" type="text" value="%s" size="60"/></a></td>""" \
        % (gene_num, getGene(gene_num)))
        if (gene_num % 10) == 0:
            app("<td><a href='#top'>Back to the top</a></td>")
        app("</tr>")            
    app("</table>")        
    app("</form>")

    return "\n".join(result)            
     
#-----------------------------------------------------------------------
# /review
# /review/001/
# /review/001/foo.png
#-----------------------------------------------------------------------
def review(directory=None,REQUEST=None):
    """Review the results"""
  
    if not directory:
        outputdir=open(CURRENT_OUTPUTDIR_PATH).read()   
        outputdir=outputdir.split('results\\')[1]
        REQUEST.response.redirect(REQUEST.URL + '/%s/' % outputdir)
        return
    #
    # Work out a path into a directory  
    #
    traverse_subpath = REQUEST.traverse_subpath
    path = os.path.join( *[RESULT_PATH, directory] + traverse_subpath)
    REQUEST['path']=path
    relative_path=os.path.join( * ([directory] + traverse_subpath) )
   
    # If correlation files need to be computed then
    # do it now
    if os.path.isdir(path):
        emmixgene.calculateCorrelationForDirectory(path)
    else:
        emmixgene.calculateCorrelationForDirectory(os.path.dirname(path))

    # if file is an image, let the image module 
    # handle it
    #
    extension=os.path.splitext(path.lower())[1]
    if extension in (".png",".svg"):
        return _heatmap(path, REQUEST)

    # if file is sstats, then use EmmixResult class
    # help in the display
    if path.lower().endswith('.sstats') or \
       path.lower().endswith('.stats'):
        return review_sstats(path, REQUEST)    
        
    if path.lower().find(".dat.cut_list") >= 0 :
        return review_list(path, REQUEST) 

    #
    # if file exists, set mime type and return the file
    # otherwise, return a directory listing
    #
    if os.path.isfile(path):
        REQUEST.response.setHeader("Mime-Type","text/html")
        body='<pre>%s</pre>' % open(path,"rb").read() 
        URL0=os.path.basename(path)
        return webutil.apply_template('review_sub.htm', locals(), globals())
    elif os.path.isdir(path): 
        if not REQUEST.URL.endswith('/'):
            REQUEST.response.setBase(REQUEST.URL+"/")
    else:
        # path is not a file and not a directory
        # try and make it a directory
        print "xxx making directory " , path, extension
        recurse_mkdir(path)

    # 
    # directory listing
    #
    files = os.listdir(path)
    import numsort
    files = numsort.sorted_copy(files)
    output = ""
    review_correlations = ""
    for file in files:

        if file.endswith(".cor") and not review_correlations:
            # allow people to review correlation heatmaps
            # if .cor files exist
            review_correlations = """<p>View correlation coefficients <a href="/review_corr_thumbnails?directory=%s">as thumbnails</a> </p>""" % relative_path
        description, show_heatmap = _file_info(file)
        if (description != "" and  show_heatmap != 0): 
            # generate heatmaps for these
            output += '''
                <a href="%(file)s">%(file)s</a> <b>%(description)s</b>
                <a href="%(file)s.png" title="png format">[heatmap]</a>
                <a href="%(file)s.svg" title="svg format">[heatmap]</a><br/>
                ''' % locals()
        elif (description !="" and  show_heatmap == 0):
            # only display the file
            output += '<a href="%s">%s</a> <b>%s</b> <br/>' % \
                    (file, file, description)

    files = os.listdir("results")
    other_directories = ""

    for file in files:

        dir_path = os.path.join("results",file)
        if os.path.isdir(dir_path):
            other_directories += '<a href="../%s/">%s</a><br/>\n' % (file, file)
    

    body = """

<h1>Review results</h1>

<h2>You are reviewing: %(path)s</h2>

<p>View heatmaps 
   <a href="/review_data_thumbnails?directory=%(relative_path)s">as thumbnails</a>
</p>

%(review_correlations)s

%(output)s

<p><a href="file://%(path)s" target="_blank">Open</a> the current results folder</p>
<hr/>

<H2>
Review results in other directories
</H2>

%(other_directories)s

<hr/>

<b>Note the following is a mock up only</b>
<h2>Logs</h2>

<font size="-1">
<TABLE>
    <TR>
        <TD>Data File
        </TD>
        <TD>Anon.dat
        </TD>
    </TR>
    <TR>
        <TD>Date run
        </TD>
        <TD>15/10/2001
        </TD>
    </TR>
    <TR>
        <TD>Researcher Notes
        </TD>
        <TD>ddd
        </TD>
    </TR>
    <TR>
        <TD>%(path)s
        </TD>
        <TD>
        </TD>
    </TR>
</TABLE>

</font>

<hr/>
""" % webutil._multimap(globals(), locals()) 
    return webutil.apply_template('review.htm', locals(), globals())

def review_data_thumbnails(directory, REQUEST):
    """Reviews all the heatmaps in a directory in a thumbnail format"""

    def check_display(file):
        description, show_heatmap = _file_info(file)
        return show_heatmap 

    body = _thumbnails(directory,check_display)
    URL0 = "Thumbnails"
    return webutil.apply_template('review_sub.htm', locals(), globals())

def review_corr_thumbnails(directory, REQUEST):
    "Reviews the thumbnails of the correlation coefficients"

    def check_display(file):
        return file.endswith(".cor") 

    body = _thumbnails(directory,check_display)        
    URL0 = "Correlation Thumbnails"
    return webutil.apply_template('review_sub.htm', locals(), globals())

def review_list(filename, REQUEST):
    """ Reviews the list file """

    results, URL0 = _getEmmixResult(filename)
    datafile = results.data_filename
    result_dir = results.result_dirname

    _html = []; html=_html.append
    html("""Edit the gene descriptions""")
    html("""<a href="/edit_gene_info?datafile=%s&result_dir=%s">here</a>.""" \
    % (datafile, result_dir))
    html("<table>")
    html("""
    <tr>
        <th align="right">Selected gene-number</th>
        <th align="right">actual gene-number</th>
        <th align="left">Gene description</th>
        <th align="left">Value</th>
    </tr>""")
    for line in open(filename, 'r').readlines():
        #
        # The list file contains spaces used for formatting
        #   eg.   45 0.0085  83  1349
        #
        # This is stripped out using the filter function
        #
        args=filter(lambda x:x, line.split(" "))
        try:
            gene_number = int(args[0])
            gene = results.getSelectedGene(gene_number)
            gene_description = gene.description
            html("""
            <tr>
                <td align="right">%s</td>
                <td align="right">%s</td>
                <td align="left">%s</td>
                <td align="left">%s</td>
            </tr>
            """ % (gene_number, gene.number, gene_description, args[1]))
        except:
            print "WARNING: review_list couldn't read - " + line[:-1]
            pass
    html("</table>")
    return "\n".join(_html)

def _getEmmixResult(filename):
    
    basename=os.path.basename(filename).lower()
    if basename.endswith('.cut.sstats'):
        datafile=basename[:-len('.cut.sstats')]
        URL0='Sorted Statistics'
    elif basename.endswith('.cut.stats'):
        datafile=basename[:-len('.cut.stats')]
        URL0='Statistics'
    elif basename.find(".dat.cut") >= 0:
        datafile=basename.split(".cut")[0]
        URL0='List data'        
    result_dir=os.path.dirname(filename)
    results=emmixgene.EmmixResult( \
        CURRENT_DATA_PATH, \
        result_dir, \
        datafile)
    return results, URL0

def review_sstats(filename, REQUEST):
    "Reviews the sstats file for a given filename"
    results, URL0 = _getEmmixResult(filename)
    datafile = results.data_filename
    result_dir = results.result_dirname
            
    html="""
    Edit the gene descriptions <a href="/edit_gene_info?datafile=%s&result_dir=%s">here</a>.
    """ % (datafile, result_dir)

    html+="""
        <table>
        <tr>
            <!--<th>n-th selected gene</th>-->
            <th>log-lambda</th>
            <th>minimum cluster size</th>
            <th>original gene number</th>
            <th>gene description</th>
        </tr>
    """
    try:
        for line in open(filename,'r').readlines():
            selected_gene_number, loglambda, minsample, gene_number = \
            filter(lambda x: x, line.split(' '))
            html+='''
            <tr>
                <!-- <td align="right">%s</td> -->
                <td align="right">%s</td>
                <td align="right">%s</td>
                <td align="right">%s</td>''' \
            % (selected_gene_number, loglambda, minsample, gene_number)
            gene=results.getSelectedGene(int(selected_gene_number))
            if gene:
                html+='<td>%s</td></tr>\n' % gene.description
            else:
                html+='<td>No description found</td></tr>\n'
        html+='</table></html>'
        body=html
    except TypeError:
        # Hmm, sstats has less than 4 columns
        body='<pre>%s</pre>' % open(filename,'r').read()
    return webutil.apply_template('review_sub.htm', locals(), globals())

def _thumbnails(directory,check_display):
    # parameters:
    #   check_display is a callback function
        
    # 
    # directory listing
    #
    import numsort
    files = os.listdir(os.path.join(RESULT_PATH,directory))
    files = numsort.sorted_copy(files)

    #
    # generate html
    #
    output = ""
    for file in files:
        if check_display(file):
            heatmap_thumb = "review/%(directory)s/%(file)s_th.png" % locals()
            heatmap_full  = "review/%(directory)s/%(file)s.png" % locals()
            output += '''<div class="box">
    <a href="%(heatmap_full)s"><img src="%(heatmap_thumb)s" border="0"></a><br/>
    <font size="-1">%(file)s</font><br/>
</div>
''' % locals()
 
    return """
    <style>
        .box {
                float: left;
                padding: 5px;
                width: 160px;
                align: center;
                font-size: 0.99em;

              }
    </style>
    %s
""" % output

#-----------------------------------------------------------------------
# run
#-----------------------------------------------------------------------
def run(select_genes=0, cluster_genes=0, cluster_tissues=0, REQUEST=None):
    "Runs the selected configuration"

    global current_rule

    try:
        # Create the output directory
        if not os.path.isdir(current_outputdir):
            recurse_mkdir(current_outputdir)
        
        #
        # copy the current rule into the output path
        #
        actual_rule_path = os.path.abspath( \
            os.path.join(current_outputdir, os.path.basename(CURRENT_RULE_PATH)))
        actual_rule = emmixgene.EmmixRule()

        if os.path.exists(actual_rule_path):
            actual_rule.restore_rule(actual_rule_path)
        if select_genes:
            actual_rule.params_select_genes = current_rule.params_select_genes
        if cluster_genes:
            actual_rule.params_cluster_genes = current_rule.params_cluster_genes
        if cluster_tissues:
            actual_rule.params_cluster_tissues = current_rule.params_cluster_tissues
        actual_rule.store_rule(actual_rule_path)

        #
        # run on the data file copied on the output path
        # note: setOutputDir() will copy source data files
        #       over to the output path
        actual_datafiles = emmixgene.EmmixDataFiles()
        actual_datafiles.restore(CURRENT_DATAFILES_PATH)
        actual_datafiles.setOutputDir(current_outputdir, \
            select_genes = select_genes, \
            cluster_genes = cluster_genes, \
            cluster_tissues = cluster_tissues)
        
        #
        # represent which routines to run as a list
        #
        routines = []
        if select_genes:
            datafile=actual_datafiles.select_genes.filename
            if not os.path.isfile(datafile):
                raise "File Not Found",datafile
            routines.append("select_genes")
        if cluster_genes:
            datafile=actual_datafiles.cluster_genes.filename
            if not os.path.isfile(datafile):
                raise "File Not Found",datafile
            routines.append("cluster_genes")
            # routines.append("docoeff") xxx check and debug
        if cluster_tissues:
            datafile=actual_datafiles.cluster_tissues.filename
            if not os.path.isfile(datafile):
                raise "File Not Found",datafile
            routines.append("cluster_tissues")

        run_thread = emmixgene.EmmixRun(current_rule, actual_datafiles, routines)
        run_thread.start()

        time.sleep(2.0) # Give a chance for processes to start
        
        if REQUEST: 
            REQUEST.response.redirect("/index_html?time=%f" % time.time())
            return ""
            
        return standard_html_header + \
        "<B>Process started</B> <br/> <a href='/'>Back to main page</a>" + \
        standard_html_footer
        
    except:
        (msg1, msg2, dummy) = sys.exc_info()
        return perror(msg1, msg2)

#-----------------------------------------------------------------------
# display_running_proc
#-----------------------------------------------------------------------

def display_running_processes():
    "Returns a list of what's running"
    
    list = []
    for program_name, data_file, stdin_file, stdout_file in \
        EmmixProcessManager.listRunningProcesses():

        list.append( """
            <tr>
            <td><a href="display_info?stdout=%s">%s</a></td>
            <td>%s</td>
            </tr>
                     """ % (stdout_file,program_name, data_file))

    body = "".join(list)
    return webutil.apply_template('running.htm', locals(), globals())

#-----------------------------------------------------------------------
# display_messages
#-----------------------------------------------------------------------

msgs = MessageStore.MessageStore('messages.txt')
emmixgene.msgs=msgs

    
def _correlation(src_filename, REQUEST):
    # returns the correlation file if available.
    # otherwise generates it.
    # fullpath eg. D:\foo\results\001\b2t.cut.group1
    # 
    corr_filename = src_filename + ".cor"
    rows = -1
    cols = -1
    cmdline = 'bin/docoeff.exe %s %d %d' % (src_filename, rows, cols)
    if not _up_to_date( src_filename, corr_filename):
        rule = emmixgene.EmmixRule()
        data = emmixgene.EmmixDataFiles(src_filename)   
        routines = ['docoeff']
        run = emmixgene.EmmixRun(rule, data, routines)    
        run.run()
        
    response = REQUEST.response
    response.setHeader("Content-Type", "text/html")
    return open( corr_filename, 'r').read()
        
def _heatmap(fullpath, REQUEST):
    # fullpath eg. D:\foo\results\001\heatmap.cut.png
    #              D:\foo\results\001\heatmap_th.cut.png
    #              D:\foo\results\001\heatmap.cut.svg
    #

    # Work out the source file for the heatmap
    # 
    heatmap_src, extension = os.path.splitext(fullpath.lower())
    if heatmap_src.endswith('_th'):
        heatmap_src = heatmap_src[:-3]
        bigpath = heatmap_src + extension
    else:
        bigpath = fullpath
        
    # The content type depends on the file extension
    if extension == ".png":
        mimetype = "image/png"
        heatmap_class = heatmap.Heatmap
    elif extension == ".svg":
        mimetype = "image/svg+xml"
        heatmap_class = heatmapsvg.Heatmap

    response = REQUEST.response
    #
    # Check that heatmap bitmap is newer than
    # the source of heatmap figures before
    # returning heatmap
    #
    if _up_to_date(heatmap_src, fullpath):
        response.setHeader("Content-Type",mimetype)
        return open(fullpath,'rb').read()
        
    if os.path.exists(heatmap_src):
        #
        # Generate heatmap on the fly
        # 
        thumbpath = "%s_th.png" % heatmap_src 
        hm = heatmap_class()
        hm.setdatafile(heatmap_src)
        #
        # fetch the gene data
        #
        result_dir,datafile=os.path.split(heatmap_src.lower())
        if datafile.endswith(".cut"):
            datafile=datafile[:-len(".cut")]
            ylabel='selected genes'
        else:
            ylabel='original data'
        gene_info=emmixgene.EmmixResult( \
            CURRENT_DATA_PATH, \
            result_dir, \
            datafile)
        if gene_info.gene_info_exists:
            if ylabel=='selected genes':
                for i in range(gene_info.getSelectedGeneCount()):
                    hm.ylabels.append(gene_info.getSelectedGene(i+1).description)
            elif ylabel=='original data':
                for i in range(gene_info.getGeneCount()):
                    hm.ylabels.append(gene_info.getGene(i+1).description)
        hm.plot(bigpath, thumbpath)
        response.setHeader("Content-Type",mimetype)
        return open(fullpath,"rb").read()
    else:
        raise "Not Found", heatmap_src

def review__bobo_traverse__(REQUEST, directory_name):
    #
    # strips away all the urls below /review/
    # if /review/foo/bar/bas
    # stores in REQUEST
    #   directory         'foo'
    #   traverse_subpath  'bar',bas'
    #

    #  
    # stores in REQUEST
    #   directory         'foo'
    REQUEST.set('directory', directory_name)

    # stores in REQUEST
    #   traverse_subpath  'bar',bas'
    #
    # If the url request is 
    #   /review/001/foo/bar
    # trns is the remainder of URL held in a list 
    # eg. ['bar','foo'] 
    # we unset it so that ZPublisher does try to
    # walk the remainder of the path
    #
    trns = REQUEST['TraversalRequestNameStack']
    REQUEST.set('traverse_subpath', trns)
    REQUEST['TraversalRequestNameStack']=[] 

    return review

review.__bobo_traverse__ = review__bobo_traverse__

def conf_select_data( \
    REQUEST, filter=None, file=None, \
    initial_file=""):
    """
    Select data file. 
    program - all, select_genes, cluster_genes, cluster_tissues
    Uses cookies to remember which program was set
    """

    program = REQUEST.form.get('program', \
              REQUEST.cookies.get('program', 'all'))
    global current_datafiles
    if not file: 
        src='/conf_select_data'
        caption = (not program != 'all' and 'select genes') or program
        REQUEST.set('current_dir','data')
        REQUEST.RESPONSE.setCookie('program',program)
        return webutil.select_path( \
            REQUEST, 
            filter=filter, 
            src=src,
            caption=caption,
            initial_file=initial_file)
    if program == 'all':
        #
        # did not specify select-genes, cluster-genes
        # or cluster-tissues
        #
        cdf=current_datafiles
        cdf.select_genes=emmixgene.EmmixData(file)        

        # set the input files for these to come
        # from the output directory
        global current_outputdir
        actual_datafile=os.path.join(current_outputdir, os.path.basename(file))
        cdf.cluster_genes=emmixgene.EmmixData(actual_datafile+'.cut')
        cdf.cluster_tissues=emmixgene.EmmixData(actual_datafile+'.cut_groupmeans')
        cdf.store(CURRENT_DATAFILES_PATH)
        
    else:
        if program in ('select_genes', \
                               'cluster_genes', \
                               'cluster_tissues'):
            setattr(current_datafiles,program,emmixgene.EmmixData(file))
            current_datafiles.store(CURRENT_DATAFILES_PATH)

    # redirect to the program page
    if program in ('select_genes', \
                           'cluster_genes', \
                           'cluster_tissues'):
        REQUEST.response.redirect('/main_%s' % program)
    else:
        REQUEST.response.redirect("/main_select_genes")
    return

def conf_select_outputdir(REQUEST, dir=None, createfolder=None):
    "Select the output directory"
    referer_id = 'conf_select_outputdir_referer'
    if not dir and not createfolder:
        REQUEST.response.setCookie( referer_id,REQUEST['HTTP_REFERER'])
        src='/conf_select_outputdir'
        return webutil.select_directory(REQUEST, rootdir="results",src=src)
    global current_outputdir
    if dir:
        current_outputdir=dir
    elif createfolder:
        current_outputdir=createfolder
        recurse_mkdir(createfolder)
    open(CURRENT_OUTPUTDIR_PATH,'w').write(current_outputdir)
    referer = REQUEST.get(referer_id, '/')
    REQUEST.response.redirect(referer)
    return

def reportBack():
    "Produces a zip file for report back"
    os.system("pkzip25 -add -dir=current report EmmixGene/* results/* configuration/*")
    return """<html><body>Report.zip has been created in %s <br/>              
              You can email this to Chui. <br/>
              <a href="/">Back to main page</a>
              
              </body>
              </html>
           """ % os.getcwd() 
           
def perror(msg1, msg2, redirect="/"):
    return \
        standard_html_header + """
        <h2>%s</h2>
        <p>%s</p>
        <form action="%s" method="get">
        <input type="submit" value="ok">
        </form>
        """ % (msg1, msg2, redirect) + standard_html_footer

def testme(REQUEST):
    "Another test"

    a=TEST()
    return a.index_html(REQUEST)

def testdtml(REQUEST):
    "Tests a file document template"

    dt = DocumentTemplate.HTMLFile('test.dtml')
    return dt(REQUEST)
 
def shutdown():
    "End"
    sys.exit(0)
 
#-----------------------------------------------------------------------
# utility functions 
#-----------------------------------------------------------------------

def _file_info(filename):
    filetype={'.dat': ('Original data set',1),
              '.cut': ('Reduced data set, filtered by select-genes',1),
              '.cor': ('Correlation coefficient',0),
              '.txt': ('Cluster-tissues output',0),
              '.gstats': ('Statistics, generated by cluster-genes',0),
              '.stats': ('Ranking, generated by select-genes',0),
              '.sstats': ('Sorted Ranking, generated by select-genes',0)}
    ext = os.path.splitext(filename)[1].lower()
    if filetype.has_key(ext):
        description, show_heatmap = filetype[ext]
    else:
        description, show_heatmap = "",0
    if ext[:-1].endswith('group')\
       or ext[:-2].endswith('group')\
       or ext.endswith('groupmeans'):
       show_heatmap = 1
       description  = "Group file"
    if ext[:-1].endswith('list') or \
       ext[:-2].endswith('list'):
       description = "List file"
    return description, show_heatmap

def _up_to_date(src_filename, dst_filename):
    # returns true if a dst_filename is up to date
    # with respect to a src_file. Kind of like "make"
    if os.path.exists(dst_filename):
        st_mtime1 = os.stat(dst_filename)[9]
    else:
        # destination file doesn't exist. 
        # pretend that the file is *very* old
        st_mtime1 = 0
    if os.path.exists(src_filename):
        st_mtime2 = os.stat(src_filename)[9]
    else:
        # source file doesn't exist. 
        # pretend that the file is *even* older 
        st_mtime2 = -1
    # file is up-to-date if destination's datetime
    # occurs after source's datetime
    return st_mtime1 >= st_mtime2

def __bobo_after__():
    import pprint
    #pprint.pprint (sys.modules)

standard_html_header = """<HTML>
<HEAD>
<TITLE>Emmix-Gene</TITLE>
<meta %(meta)s>
</HEAD>
<BODY>
<h1><a href="/">Emmix-Gene</a></h1>
<HR/>
<DIV ALIGN="RIGHT">
Configuration | <A HREF="/shutdown">Quit</A>
</DIV>"""

standard_html_footer = """
</BODY>
</HTML>
"""

webutil.standard_html_header=standard_html_header
webutil.standard_html_footer=standard_html_footer

images=webutil.FileSystemDirectory('images')
#vi:ts=4:et:softtabstop=4

