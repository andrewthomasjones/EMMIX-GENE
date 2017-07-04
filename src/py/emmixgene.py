# (c) Department of Mathematics,
#     University of Queensland
#     2002
#
# $Log: emmixgene.py,v $
# Revision 1.16  2003/07/08 06:28:47  chui.tey
# Use original data file for the number of genes
#
# Revision 1.15  2003/06/27 16:28:52  chui.tey
# Do not includes gene number 0
#
# Revision 1.14  2003/06/27 15:21:55  chui.tey
# *** empty log message ***
#
# Revision 1.12  2002/12/27 10:24:45  default
# Bug fix for _copy_cmdline_output
#
# Revision 1.11  2002/12/27 10:14:06  default
# Copy stdout with nice file name
#
# Revision 1.10  2002/12/27 09:47:01  default
# Use recurse_mkdir, copies stdout to result directories
#
# Revision 1.9  2002/12/27 08:27:16  default
# Moved select-genes.py to bin directory
#
# Revision 1.8  2002/09/22 05:36:19  default
# Added gene_info_exists property
# Added getGeneCount, getSelectedGeneCount
#
# Revision 1.7  2002/09/15 09:46:58  default
# Introduced EmmixResult class - which links cut genes with original
# number, and reads the gene descriptions from a flat file in the
# data directory
#
# Revision 1.6  2002/07/03 13:14:16  default
# Use relative paths for docoeff so that spaces in path names don't break the program
#
# Revision 1.5  2002/06/29 11:02:18  default
# Introduced docoeff.exe
#
# Revision 1.4  2002/05/04 02:17:27  default
# Safe and selective copying of data files depending on
# whether select-genes, cluster-genes or cluster-tissues is run
#
# Revision 1.3  2002/04/10 20:42:08  default
# Bug fix: sharing common instance of default_params
# Bug fix: function names mispelled
# Refactored: restore_rule factory function
#
# Revision 1.2  2002/04/03 10:20:02  default
# Non-source files removed
#
# Revision 1.1.1.1  2002/04/02 13:56:26  default
# Initial checkin
#
#
#--------------------------------------------------------------------------
# public functions
#--------------------------------------------------------------------------

import os
import shelve
import shutil
import threading 
import EmmixProcessManager
import MessageStore
import time
from pathutils import safecopy

def restore_rule(filename):

    """Loads an EmmixRule from a configuration file"""

    rule=EmmixRule()
    rule.restore_rule(filename)
    return rule
    
    #d = shelve.open(filename)
    #instance = d['EmmixRule']
    #d.close()
    #return instance

def restore_datafiles(filename):

    """Loads an EmmixDataFiles from a configuration file"""
    
    d = EmmixDataFiles()
    d.restore(filename)
    return d

#--------------------------------------------------------------------------
# class EmmixDataFiles
#   a dictionary of data files for each program
# example:
#   f = EmmixDataFiles()
#   f.restore(filename)
#   emmixdata = f['select_genes']
#   emmixdata = f['cluster_genes']
#   emmixdata = f['cluster_tissues']
# methods:
#   setOutputDir(path)
#   store(filename)
#   restore(filename)
#--------------------------------------------------------------------------

class EmmixDataFiles:

    def __init__(self, filename=''):

        emmixdata = EmmixData(filename)
        self.select_genes=emmixdata
        self.cluster_genes=emmixdata
        self.cluster_tissues=emmixdata
        self.docoeff=emmixdata

    def setOutputDir(self, outputdir, \
        select_genes = 0, \
        cluster_genes = 0, \
        cluster_tissues = 0):

        self.outputdir=outputdir

        file1=os.path.basename(self.select_genes.filename)
        file2=os.path.basename(self.cluster_genes.filename)
        file2sstats=os.path.basename(self.cluster_genes.filename+'.sstats')
        file3=os.path.basename(self.cluster_tissues.filename)
        
        file1=os.path.join(outputdir, file1)
        file2=os.path.join(outputdir, file2)
        file2sstats=os.path.join(outputdir, file2sstats)
        file3=os.path.join(outputdir, file3)

        #
        # copy source data files to output path
        #
        if select_genes:
            safecopy(self.select_genes.filename, file1)
        if cluster_genes:
            safecopy(self.cluster_genes.filename, file2)
            sstats = self.cluster_genes.filename+'.sstats'
            safecopy(sstats, file2sstats)
        if cluster_tissues:
            safecopy(self.cluster_tissues.filename, file3)

        self.select_genes=EmmixData(file1)
        self.cluster_genes=EmmixData(file2)
        self.cluster_tissues=EmmixData(file3)

    def store(self, filename):

        d = shelve.open(filename)
        d['select_genes'] = self.select_genes
        d['cluster_genes'] = self.cluster_genes
        d['cluster_tissues'] = self.cluster_tissues
        d['docoeff'] = self.docoeff
        d.close()

    def restore(self, filename):

        try:
            d = shelve.open(filename)
            if d.has_key('select_genes'):self.select_genes=d['select_genes']
            if d.has_key('cluster_genes'):self.cluster_genes=d['cluster_genes']
            if d.has_key('cluster_tissues'):self.cluster_tissues=d['cluster_tissues']
            if d.has_key('docoeff'):self.docoeff=d['docoeff']
            d.close()
        except:
            pass

        return
        print "Check assertions"
        print "Docoeff filename = " + self.docoeff.filename
        assert self.select_genes.filename
        assert self.cluster_genes.filename
        assert self.cluster_tissues.filename
        assert self.docoeff.filename
        
#--------------------------------------------------------------------------
# class EmmixData
# one single input file
# methods:
#   get_kwargs
#--------------------------------------------------------------------------

class EmmixData:

    def __init__(self, filename, rows=None, cols=None):

        self.filename = filename
        
        #
        # Try autodetect the number of rows and columns
        # If the file does not exist, then do it later, 
        # during get_kwargs
        #
        if not rows or not cols:
            if os.path.isfile(self.filename):
                (auto_rows, auto_cols) = _autodetect(self.filename)
            else:
                auto_rows = None
                auto_cols = None
                
        if rows:
            self.rows = rows
        else:
            self.rows = auto_rows
        if cols:
            self.cols = cols
        else:
            self.cols = auto_cols

    def get_kwargs(self):

        #
        # _autodetect() autodetects number of rows, columns
        # in a file
        #
        if not self.rows or not self.cols:
            if not os.path.isfile(self.filename):
                raise "FileNotFound", "Data file %s missing" % self.filename 
            (auto_rows, auto_cols) = _autodetect(self.filename)

            self.rows=auto_rows
            self.cols=auto_cols

        args = {}
        args['filename'] = self.filename
        args['rows'    ] = self.rows
        args['cols'    ] = self.cols
        return args

    def store_data(self, filename):

        d= shelve.open(filename)
        d['EmmixData']=self
        d.close()

    def restore_data(self, filename):
        try:
          d= shelve.open(filename)
          newself=d['EmmixData']
          d.close()
          self._dict__=newself._dict__
        except:
          pass


#--------------------------------------------------------------------------
# class EmmixRule
# encapsulates all the parameters that go into processing a data file
# attributes:
#    too many to list, example:
#    params_select_genes['random_seed1']
#    params_select_genes['random_seed2']
#    params_select_genes['random_seed3']
#
# methods:
#    start_select_genes( myEmmixData )
#    start_cluster_genes( myEmmixData )
#    start_cluster_tissues( myEmmixData )
#    store_rule( filename )
#    restore_rule( filename )
#    existsSelectGenesResults(myEmmixData)
#    existsClusterGenesResults(myEmmixData)
#    existsClusterTissuesResults(myEmmixData)
#--------------------------------------------------------------------------

class EmmixRule:

    """EmmixGene processing parameters"""

    default_params_select_genes = {
        'random_starts' : 4,
        'kmean_starts'  : 4, 
        'random_seed1'  : 1234,
        'random_seed2'  : 2345,
        'random_seed3'  : 4567,
        'threshold_likelihood' : 8,
        'threshold_clustersize': 8,
        'num_rows': 0,
        'resume': 0
    }

    default_params_cluster_genes = {
        'random_starts' : 4,
        'kmean_starts'  : 4, 
        'random_starts_spherical' : 8,
        'kmean_starts_spherical'  : 8, 
        'cluster_groups'          : 20,  
        'threshold_clustersize'   : 8, 
        'random_seed1'  : 1234,
        'random_seed2'  : 2345,
        'random_seed3'  : 4567,
        'reorder'       : 'y',
        'robust'        : 'y',
        'nu'            : 1,
        'num_rows'      : 0 
    }

    default_params_cluster_tissues = {
        'num_factors'   : 4,
        'num_components': 4, 
        'random_starts' : 4,
        'kmean_starts'  : 4, 
        'random_seed1'  : 1234,
        'random_seed2'  : 2345,
        'random_seed3'  : 4567,
        'num_rows'      : 0,
        'use_factor_analyzers': 0
    }

    def __init__(self):

        self.params_select_genes = {}
        self.params_cluster_genes = {}
        self.params_cluster_tissues = {}
        self.params_select_genes.update(EmmixRule.default_params_select_genes)
        self.params_cluster_genes.update(EmmixRule.default_params_cluster_genes)
        self.params_cluster_tissues.update(EmmixRule.default_params_cluster_tissues)
        
    def existsSelectGenesResults(self, emmix_data):
        pass

    def existsClusterGenesResults(self, emmix_data):
        pass

    def existsClusterTissuesResults(self, emmix_data):
        pass

    def start_select_genes(self, emmix_data):

        args = emmix_data.get_kwargs()
        args.update( self.params_select_genes )
        # 
        # If top n rows specified by user
        # use that instead
        #
        if args['num_rows']:
            args['rows'] = int(args['num_rows'])
        del args['num_rows']
        cmdline = self.select_genes(**args)
        EmmixProcessManager.spawn(self, emmix_data, cmdline)

        # spawn is synchronous
        # so by now, select-genes has completed.
        # copy the output file to the result directory
        #
        reportname = "%s-select-genes.txt" % \
            os.path.basename(emmix_data.filename)[:3].upper()
        _copy_stdout(cmdline, os.path.dirname(emmix_data.filename), reportname)

    def start_cluster_genes(self, emmix_data):

        args = emmix_data.get_kwargs()
        args.update( self.params_cluster_genes )
        # 
        # If top n rows specified by user
        # use that instead
        #
        if args['num_rows']:
            args['rows'] = int(args['num_rows'])
        del args['num_rows']
        cmdline = self.cluster_genes(**args)
        EmmixProcessManager.spawn(self, emmix_data, cmdline)
        
        # spawn is synchronous
        # so by now, cluster-genes has completed.
        # copy the output file to the result directory
        #
        reportname = "%s-cluster-genes.txt" % \
            os.path.basename(emmix_data.filename)[:3].upper()
        _copy_stdout(cmdline, os.path.dirname(emmix_data.filename), reportname)
        
    def start_cluster_tissues(self, emmix_data):

        args = emmix_data.get_kwargs()
        args.update( self.params_cluster_tissues )
        # 
        # If top n rows specified by user
        # use that instead
        #
        if args['num_rows']:
            args['rows'] = int(args['num_rows'])
        del args['num_rows']
        cmdline = self.cluster_tissues(**args)
        EmmixProcessManager.spawn(self, emmix_data, cmdline)

        # spawn is synchronous
        # so by now, cluster-tissues has completed.
        # copy the output file to the result directory
        #
        reportname = "%s-cluster-tissues.txt" % \
            os.path.basename(emmix_data.filename)[:3].upper()
        _copy_stdout(cmdline, os.path.dirname(emmix_data.filename), reportname)

    def start_docoeff(self, emmix_data):

        args = emmix_data.get_kwargs()
        args['output_filename'] = args['filename'] + ".cor"
        cmdline = self.docoeff(**args)
        EmmixProcessManager.spawn(self, emmix_data, cmdline)

    def docoeff(self, output_filename, filename, rows=None, cols=None):
        """Returns the commandline required to run docoeff"""
        
        cmdline = "bin\\docoeff.exe %(filename)s %(rows)s %(cols)s > %(output_filename)s" % locals()
        return cmdline

    def select_genes(self, random_starts, kmean_starts, \
                     random_seed1, random_seed2, random_seed3,
                     threshold_likelihood, threshold_clustersize, \
                     filename, resume, rows=None, cols=None):
        """Returns a commandline necessary to run select genes with
         the given parameters"""
    
        s =  ""
        s += str(int(random_starts)) + "\n"
        s += str(int(kmean_starts))  + "\n"
        s += str(int(random_seed1))  + "\n"
        s += str(int(random_seed2))  + "\n"
        s += str(int(random_seed3))  + "\n"
        s += str(float(threshold_likelihood))  + "\n"
        s += str(int(threshold_clustersize)) + "\n"

        if resume:
            s += "y\n"
        else:
            s += "n\n"
    
        filein = 'temp\\sginput.%d' % _random_pid() 
        fileout= 'temp\\sgoutput.%d' % _random_pid()
        open( filein, 'w').write(s)

        if 0:
            cmdline = "bin\\select-genes.exe %s %d %d < %s" % \
              (filename, rows, cols, filein)
   
        else:
            cmdline = "bin\\python.exe bin\\select-genes.py %s %d %d <%s > %s" % \
             (filename, rows, cols, filein, fileout)

        return cmdline 

    def cluster_genes(self, random_starts, kmean_starts, \
                      random_starts_spherical, kmean_starts_spherical, \
                      cluster_groups, \
                      threshold_clustersize, 
                      random_seed1, random_seed2, random_seed3,
                      reorder, robust, nu, \
                      filename, rows=None, cols=None):
        "doc string"
    
        s =  ""
        s += str(int(random_starts))           + "\n"
        s += str(int(kmean_starts))            + "\n"
        s += str(int(random_starts_spherical)) + "\n"
        s += str(int(kmean_starts_spherical))  + "\n"
        s += str(int(cluster_groups))          + "\n"
        s += str(int(threshold_clustersize))   + "\n"
        s += str(int(random_seed1)) + "\n"
        s += str(int(random_seed2)) + "\n"
        s += str(int(random_seed3)) + "\n"
        s += reorder + "\n"
        s += robust  + "\n"
        if robust.lower().startswith("y"):
            s += str(nu) + "\n"

        filein = 'temp\\cginput.%d' %  _random_pid()
        fileout= 'temp\\cgoutput.%d' % _random_pid()
        open(filein, 'w').write(s)

        cmdline = "bin\\cluster-genes.exe %s %d %d < %s > %s" % \
              (filename, rows, cols, filein, fileout)
        return cmdline 
        
    def cluster_tissues(self, num_factors, num_components, \
                        random_starts, kmean_starts, \
                        random_seed1, random_seed2, random_seed3, \
                        filename, rows=None, cols=None, \
                        use_factor_analyzers=0):
        "doc string"
    
        s =  ""
        # Enter 1 to use factor analyzers, 2 to use EMMIX
        if use_factor_analyzers:
            s += "1\n"
            s += str(int(num_factors))+ "\n"
        else:
            s += "2\n"
        s += str(int(num_components)) + "\n"
        s += str(int(random_starts))  + "\n"
        s += str(int(kmean_starts))   + "\n"
        s += str(int(random_seed1))   + "\n"
        s += str(int(random_seed2))   + "\n"
        s += str(int(random_seed3))   + "\n"
        s += "cluster-tissues.txt\n"
        
        filein = 'temp\\ctinput.%d' % _random_pid() 
        fileout= 'temp\\ctoutput.%d' % _random_pid()
        open(filein, 'w').write(s)

        cmdline = "bin\\cluster-tissues.exe %s %d %d < %s > %s" % \
              (filename, rows, cols, filein, fileout)
   
        return cmdline 

    def store_rule(self, filename):

        d = shelve.open(filename)
        d['EmmixRule'] = self
        d.close()

    def restore_rule(self, filename):
       
        try:
            d = shelve.open(filename)
            newself = d['EmmixRule']
            d.close() 
            self.params_select_genes.update(newself.params_select_genes)
            self.params_cluster_genes.update(newself.params_cluster_genes)
            self.params_cluster_tissues.update(newself.params_cluster_tissues)
        except ImportError:
            # can't restore old emmixgene classes
            # we've moved them
            print "Warning: Could not restore previous rule"
            pass

#--------------------------------------------------------------------------
# class EmmixRun(Thread)
# methods:
#    __init__(emmixrule)
#    run()
#    store(filename)
#    restore(filename)
#--------------------------------------------------------------------------

class EmmixRun(threading.Thread):
    """A series of run instructions, which are executed
       in a style of a makefile.
    """

    def __init__(self, emmixrule, emmixdata, routines):
        
        threading.Thread.__init__(self)
        self.emmixrule=emmixrule
        self.emmixdata=emmixdata
        self.routines=routines

    def run(self):
        """Launches the sequence of analysis.
        """

        global msgs

        #
        # ideally, we should check whether an identical rule
        # has been run, and if so, just take the user to
        # the results
        #
        
        # Clean the proc mgr db of old pids
        EmmixProcessManager.update()
       
        #
        # see if current emmixrule is being run
        #
        emmixrule=self.emmixrule
        emmixdata=self.emmixdata.select_genes
        if "select_genes" in self.routines and \
            not EmmixProcessManager.isRunning(emmixrule, emmixdata):
            #
            # Launch program
            #
            emmixrule.start_select_genes( emmixdata )
            if 1:
            #while 1:
            #    time.sleep(5.0) # 5 seconds
            #    if not EmmixProcessManager.isRunning(emmixrule, emmixdata):
                    #
                    # Wait until process completes
                    #
                    now = time.strftime("%a %x %X", time.localtime())
                    msgs.addMessage("%s \n select genes completed" % now)
                    msgs.store()
            #       break
        emmixdata=self.emmixdata.cluster_genes
        if "cluster_genes" in self.routines and \
            not EmmixProcessManager.isRunning(emmixrule, emmixdata):
            emmixrule.start_cluster_genes( emmixdata )
            directory = os.path.dirname( emmixdata.filename )
            calculateCorrelationForDirectory( directory )
            now = time.strftime("%a %x %X", time.localtime())
            msgs.addMessage("%s \n cluster genes completed" % now)
            msgs.store()
        emmixdata=self.emmixdata.cluster_tissues
        if "cluster_tissues" in self.routines and \
            not EmmixProcessManager.isRunning(emmixrule, emmixdata):
            emmixrule.start_cluster_tissues( emmixdata )
            if 1:
            #while 1:
            #    time.sleep(5.0) # 5 seconds
            #    if not EmmixProcessManager.isRunning(emmixrule, emmixdata):
                    #
                    # Wait until process completes
                    #
                    now = time.strftime("%a %x %X", time.localtime())
                    msgs.addMessage("%s \n cluster tissues completed" % now)
                    msgs.store()
            #       break
            try:
                output_path = os.path.split(emmixdata.filename)[0]
                shutil.copy('cluster-tissues.txt',output_path)
            except:
                pass
        emmixdata=self.emmixdata.docoeff
        if "docoeff" in self.routines and \
            not EmmixProcessManager.isRunning(emmixrule, emmixdata):
            emmixrule.start_docoeff( emmixdata )

        # Get messages from EmmixProcessManager
        for message in EmmixProcessManager.messages:
            msgs.addMessage(message)
            msgs.store()
        EmmixProcessManager.messages=[]
        return 
 
    def store(self, filename):
        pass

    def restore(self, filename):
        pass

#--------------------------------------------------------------------------
#   class EmmixResult
#   synopsis:
#       e=EmmixResult('D:/client/emmix/data',
#                     'D:/client/emmix/results/001',
#                     'alon_norm.dat')
#       g=e.getSelectedGene(253)
#       # -- alon.norm.dat.cut.sstats
#       # 253 345.9480000 3 1032
#       # -- alon.norm.genes
#       # 1032 MCON255 Drosophilia Wing Colour
#       print g 
#       # outputs
#       # (1032,"MCON255 Drosophilia Wing Colour")
#--------------------------------------------------------------------------
class EmmixResult:

    def __init__(self, data_dirname, result_dirname, data_filename):

        # the data filename must end with .dat
        if not data_filename.endswith(".dat") and data_filename.find(".dat"):
            data_filename=data_filename.split(".dat")[0]+".dat"
        self.data_dirname=data_dirname
        self.result_dirname=result_dirname
        self.data_filename=data_filename
        self.sstats_filename=os.path.join( \
            result_dirname,data_filename + '.cut.sstats')
        self.genes_filename=os.path.join( \
            data_dirname,data_filename + '.genes')
        self.gene_info_exists=0            
        self._sstats={} # map of selectedGeneNum -> geneNum
        self._genes={}  # map of geneNum -> gene
        self._read_sstats_file()
        self._read_genes_file()

    def getSelectedGene(self,selectedNumber):
        if self._sstats.has_key(selectedNumber):
            geneNumber=self._sstats[selectedNumber]
            if self._genes.has_key(geneNumber):
                gene=self._genes[geneNumber]
                return gene
        return Gene(selectedNumber, "No description found")

    def getGene(self, geneNumber):
        if self._genes.has_key(geneNumber):
            gene=self._genes[geneNumber]
            return gene
        else:
            return Gene(geneNumber, "No description found")
        
    def getGeneCount(self):
        "Returns the number of genes in the original data file"
        return self._gene_count

    def getSelectedGeneCount(self):
        "Returns the number of genes selected"
        return len(self._sstats)

    def _read_sstats_file(self):
        # populate from sstats if present
        if os.path.exists(self.sstats_filename):
            for line in open(self.sstats_filename, 'r').readlines():
                try:
                    selectedNumber,log_lambda, samples_count, geneNumber = \
                    line.split(' ',3)
                    self._sstats[int(selectedNumber)]=int(geneNumber)
                except ValueError:
                    # less than three fields. Cant use
                    pass
        else:
            print "warn: %s not found" % self.sstats_filename

    def _read_genes_file(self):
        #
        # .genes files are in the format
        # 1032 MCON255 Drosophilia Wing Colour
        #
        data_filename = os.path.join(self.data_dirname, self.data_filename)
        self._gene_count = gene_count = len(open(data_filename,'r').readlines())

        if os.path.exists(self.genes_filename):
            for line in open(self.genes_filename, 'r').readlines():
                try:
                    geneNumber,geneDescription=line.split(' ',1)
                    geneNumber = int(geneNumber)
                    if geneNumber >= 1:
                        new_gene=Gene(geneNumber,geneDescription)
                        self._genes[geneNumber]=new_gene
                except: pass                    
            self.gene_info_exists=1
        else:
            genes=self._genes
            for i in range(gene_count):
                genes[i+1]=Gene(i+1, "")
            self.gene_info_exists=0
            print "warn: %s not found" % self.genes_filename
            
class Gene:
    """Gene expression description"""
    
    def __init__(self, number, description):
        self.number=number
        self.description=description

    def __repr__(self):
        return '<Gene instance. %d "%s">' % (self.number, self.description)

    def __str__(self):
        return self.description

#--------------------------------------------------------------------------
# private functions
#--------------------------------------------------------------------------

def _autodetect(filename):

    """Autodetects number of rows and columns in a text file,
    returns (numrows, numcols)"""
    
    lines=open(filename, 'r').readlines()
    
    rows=len(lines)
    if rows==0:
        cols=0
    else:
        cols=len(lines[0].split())

    return (rows, cols)

__random_pid=0
def _random_pid():
    global __random_pid
    if __random_pid==0:
        import whrandom
        __random_pid = whrandom.randrange(10000)
    __random_pid += 1
    return __random_pid

msgs = MessageStore.MessageStore('messages.txt')

def calculateCorrelationForDirectory(directory):
    for file in os.listdir(directory):
        if _isgroupfile(file):
            src_filename = os.path.join(directory, file)
            src_filename = _getRelativePath(src_filename)
            dst_filename = src_filename + ".cor"
            if not _up_to_date(src_filename, dst_filename):
                rule = EmmixRule()
                data = EmmixDataFiles(src_filename)   
                routines = ['docoeff']
                thread = EmmixRun(rule, data, routines)    
                thread.start()

def _getRelativePath(filename):
    #
    # returns relative path of filename to current
    # working directory
    #
    filename_list = [filename, os.getcwd()]
    commonprefix = os.path.commonprefix(filename_list)
    if commonprefix:
        if not os.path.isdir(commonprefix):
            commonprefix=os.path.dirname(commonprefix)
        commonprefix+=os.sep
        relative_path = os.path.join(os.curdir, filename[len(commonprefix):])
        return relative_path
    else:
        return filename
        
def _isgroupfile(filename):
    # strip away remaining digits
    if filename.isdigit():
        return 0
    while filename[-1].isdigit():
        filename=filename[:-1]
    return filename.endswith('_group') or filename.endswith('_groupmeans')

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

def _copy_stdout(cmdline, dstdir, filename):        
    outputfile = cmdline.split(">")[-1].strip()
    if os.path.isfile(outputfile):
        new_outputfile = os.path.join( dstdir, filename )
        safecopy(outputfile, new_outputfile )

#--------------------------------------------------------------------------
# simple, and by no means complete, regression test
#--------------------------------------------------------------------------

if __name__ == "__main__":

    rule = EmmixRule()

    # Example of how to set parameters
    rule.params_select_genes['random_seed1']=2345 
    rule.params_select_genes['random_seed2']=3456 
    rule.params_select_genes['random_seed3']=5678 

    data = EmmixData('teyc_test.dat')
    rule.start_select_genes(data)
    rule.start_cluster_genes(data)
    rule.start_cluster_tissues(data)

# vim: et:shiftwidth=4:softtabstop=4
