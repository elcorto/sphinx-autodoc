#!/usr/bin/env python

import importlib, inspect, pkgutil, os, optparse, shutil
import textwrap, re
pj = os.path.join

def backup(src, prefix='.'):
    """Backup (copy) `src` to <src><prefix><num>, where <num> is an integer
    starting at 0 which is incremented until there is no destination with that
    name.
    
    Symlinks are handled by shutil.copy() for files and shutil.copytree() for
    dirs. In both cases, the content of the file/dir pointed to by the link is
    copied.

    Parameters
    ----------
    src : str
        name of file/dir to be copied
    prefix : str, optional
    """
    if os.path.isfile(src):
        copy = shutil.copy 
    elif os.path.isdir(src):
        copy = shutil.copytree
    else:
        raise StandardError("source '%s' is not file or dir" %src)
    idx = 0
    dst = src + '%s%s' %(prefix,idx)
    while os.path.exists(dst):
        idx += 1
        dst = src + '%s%s' %(prefix,idx)
    # sanity check
    if os.path.exists(dst):
        raise StandardError("destination '%s' exists" %dst)
    else:        
        copy(src, dst)


def file_write(fn, txt):
    fd = open(fn, 'w')
    fd.write(txt)
    fd.close()


def format_name(name):
    """Prepend 3 wite spaces. Used for rst directive content formatting."""
    return '   %s' %name


def format_names(names):
    txt = ''
    for nn in names:
        txt += '   %s\n' %nn
    return txt    


def is_mod_member(name, obj, modname=None):
    """True if `obj` appears to be some kind of callable or class."""
    # normal python module case
    if (modname is not None) and hasattr(obj, '__module__'):
        return (inspect.isfunction(obj) or \
                inspect.isclass(obj) or \
                hasattr(obj, '__call__')) and \
                obj.__module__ == modname
    # extension module (only f2py tested), very flaky test ...            
    else:
        return (not name.startswith('__')) and \
               (not inspect.ismodule(obj)) and \
                hasattr(obj, '__doc__')


class Module(object):
    """Represent a module in a package and various formes of its name. Write
    RST files into a sphinx source path based on templates.
    
    Notes
    -----
    Variable names and module related names:

    source        = pkgname
    name          = pkgname.sub1.sub2.basename
    fullbasename  = sub1.sub2.basename
    """
    def __init__(self, name, source='source', apipath='generated/api',
                 docpath='generated/doc'):
       
        self.api_templ = textwrap.dedent("""
        .. rst file which lists all members of the current module. They will be
        .. handled by the Sphinx autosummary extension.

        {fullbasename}
        {bar}

        .. currentmodule:: {name}

        .. autosummary::
           :toctree:
           
        {members}
        """)
        
        self.doc_templ = textwrap.dedent("""
        .. rst file to pull only module doc strings at the top of the
        .. module file. These usually contain short tutorial-like stuff about what
        .. can be done with the module's content.

        .. In each module doc string, create at least one heading such that sphinx
        .. picks it up. We use automodule with :no-members: to render only the module
        .. doc string.

        {fullbasename}
        {bar}

        .. automodule:: {name}
           :no-members:
        """)
        self.name = name
        self.source = source
        self.apipath = apipath
        self.docpath = docpath
        for p in [self.docpath, self.apipath]:
            pp = pj(self.source, p)
            if not os.path.exists(pp):
                os.makedirs(pp)
        spl = self.name.split('.')
        self.pkgname = spl[0]
        self.basename = spl[-1]
        self.fullbasename = '.'.join(spl[1:])
        self.bar = "="*len(self.fullbasename)
        self.obj = importlib.import_module(name)
        assert inspect.ismodule(self.obj)
        self.sourcefile = inspect.getsourcefile(self.obj)
        self.members = \
            [x[0] for x in inspect.getmembers(self.obj) if \
             is_mod_member(x[0], x[1], self.name)]
        self.has_doc = False
        if self.sourcefile is not None:
            fh = open(self.sourcefile)
            lines = fh.readlines()[:3]
            fh.close()
            for ll in lines:
                if ll.startswith('"""'):
                    self.has_doc = True
                    break
    
    def write_api(self):
        """Write source/generated/apipath/module.rst"""
        txt = self.api_templ.format(members=format_names(self.members), 
                                    fullbasename=self.fullbasename,
                                    name=self.name, bar=self.bar)
        file_write(pj(self.source, 
                      self.apipath, 
                      self.fullbasename) + '.rst', txt)
    
    def write_doc(self):
        """Write source/generated/docpath/module.rst"""
        if self.has_doc:
            txt = self.doc_templ.format(fullbasename=self.fullbasename,
                                        name=self.name, bar=self.bar)
        file_write(pj(self.source, 
                      self.docpath, 
                      self.fullbasename) + '.rst', txt)


def walk_package(pkg, mod_names=[]):
    """Walk thru a Python package and return all module names.
    
    Parameters
    ----------
    pkg : imported package object (e.g. ``import scipy``).
    
    Returns
    -------
    names : list
        List of module names, e.g. ``['scipy.linalg.inv',
        'scipy.linalg.norm',...]``.
    """
    for loader, name, ispkg in pkgutil.iter_modules(pkg.__path__, 
                                                    prefix=pkg.__name__ + '.'): 
        if ispkg:
            mod_names = walk_package(importlib.import_module(name),
                                     mod_names=mod_names)
        else:    
            mod_names.append(name)
    return mod_names 


if __name__ == '__main__':
    
    import sys, optparse
    api_index_templ = textwrap.dedent("""
    .. generated API doc index file

    API Reference
    -------------
    
    .. toctree::
       :maxdepth: 1

    {modules_api}
    """)
    
    doc_index_templ = textwrap.dedent("""
    .. doc strings from modules index file
    
    Documentation from modules
    --------------------------
    
    .. toctree::
       :maxdepth: 3

    {modules_doc}
    """)
    
    written_index_templ = textwrap.dedent("""
    .. index for hand-written docu. Anything below {writtenpath}/ will not be
    .. overwritten, here you can place hand-written rst files, and list them 
    .. in {writtenpath}/index.rst
     
    More Topics
    -----------
   
    .. toctree::
       :maxdepth: 1 
       
       {writtenpath}/index
    """)
    
    index_templ = textwrap.dedent("""
    {package_name}
    {bar}

    Table of contents
    -----------------
    .. toctree::
       :maxdepth: 1
    
       {apipath}/index
       {docpath}/index
    """)
    
    parser = optparse.OptionParser(\
        usage = textwrap.dedent("""\
        usage: %prog [options] <package>

        Arguments:
            package : The name of the package to walk (e.g 'scipy')
        """))

    parser.add_option('-s', '--source', action='store',
                      help='sphinx source dir below which all rst files will \
                      be written [%default]', default='source')
    parser.add_option('-a', '--apipath', action='store',
                      help="""dir for generated API rst files (relative to \
                      SOURCE) [%default]""", default='generated/api')
    parser.add_option('-d', '--docpath', action='store',
                      help="""dir for generated rst files for doc strings
                      pulled from modules (relative to \
                      SOURCE) [%default]""", default='generated/doc')
    parser.add_option('-w', '--writtenpath', action='store', 
                      help="""dir for hand written rst files, an index.rst file
                      must exist there (relative to \
                      SOURCE) [%default]""", default='written')
    parser.add_option('-i', '--write-index', action='store_true', 
                      help="""(over)write SOURCE/index.rst [%default]""", 
                      default=False)
    parser.add_option('-X', '--exclude', 
                      help="""regex for excluding modules, applied to the full
                      module name [%default]""", 
                      default=None)
    
    (opts, args) = parser.parse_args(sys.argv[1:])
    
    package_name = args[0]
    bar = '='*len(package_name)
    print("processing package: %s" %package_name)
    package = importlib.import_module(package_name)
    mods = [Module(name, source=opts.source, apipath=opts.apipath,
                   docpath=opts.docpath) for name in walk_package(package)]
    if opts.exclude is not None:
        rex = re.compile(opts.exclude)
        mods = [mod for mod in mods if rex.search(mod.name) is None]
    modules_api = ''
    modules_doc = ''
    print "modules:"
    for mod in mods:
        print("  %s" %mod.name)
        mod.write_api()
        modules_api += format_name(mod.fullbasename) + '\n'
        if mod.has_doc:
            mod.write_doc()
            modules_doc += format_name(mod.fullbasename) + '\n'
    
    txt = api_index_templ.format(modules_api=modules_api)
    file_write(pj(opts.source, opts.apipath, 'index.rst'), txt)

    txt = doc_index_templ.format(modules_doc=modules_doc)
    file_write(pj(opts.source, opts.docpath, 'index.rst'), txt)
    
    if opts.write_index:
        index_fn = pj(opts.source, 'index.rst')
        print "overwriting main index: %s" %index_fn
        if os.path.exists(pj(opts.source, opts.writtenpath)):
            index_templ += written_index_templ
        txt = index_templ.format(apipath=opts.apipath, docpath=opts.docpath,
                                 writtenpath=opts.writtenpath,
                                 package_name=package_name, bar=bar)
        if os.path.exists(index_fn):
            backup(index_fn)
        file_write(index_fn, txt)

