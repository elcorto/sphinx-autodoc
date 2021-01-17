import argparse
import importlib
import inspect
import os
import pkgutil
import re
import shutil
import textwrap

pj = os.path.join


def _backup(src, prefix="."):
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
        raise Exception("source '%s' is not file or dir" % src)
    idx = 0
    dst = src + "%s%s" % (prefix, idx)
    while os.path.exists(dst):
        idx += 1
        dst = src + "%s%s" % (prefix, idx)
    # sanity check
    if os.path.exists(dst):
        raise Exception("destination '%s' exists" % dst)
    else:
        copy(src, dst)


def file_write(fn, txt, backup=False):
    if os.path.exists(fn):
        if backup:
            _backup(fn, prefix=".bak")
        else:
            raise Exception(f"file exists: {fn}")
    with open(fn, "w") as fd:
        fd.write(txt)


def format_name(name):
    """Prepend 3 wite spaces. Used for rst directive content formatting."""
    return f"   {name}"


def format_names(names):
    return '\n'.join(f"   {nn}" for nn in names)


def is_mod_member(name, obj, modname=None):
    """True if `obj` appears to be some kind of callable or class."""
    # normal python module case
    if (modname is not None) and hasattr(obj, "__module__"):
        return (
            inspect.isfunction(obj)
            or inspect.isclass(obj)
            or hasattr(obj, "__call__")
        ) and obj.__module__ == modname
    # extension module (only f2py tested), very flaky test ...
    else:
        return (
            (not name.startswith("__"))
            and (not inspect.ismodule(obj))
            and hasattr(obj, "__doc__")
        )


class Module:
    """Represent a module in a package and various forms of its name. Write
    RST files into a sphinx source path based on templates.

    Notes
    -----
    Variable names and module related names:

    name          = pkgname.sub1.sub2.basename
    fullbasename  = sub1.sub2.basename
    """

    def __init__(
        self,
        name,
        source="source",
        apipath="generated/api",
        docpath="generated/doc",
    ):

        # source/apipath/genname.rst
        self.api_templ = textwrap.dedent(
            """
        .. rst file which lists all members of the current module. They will be
        .. handled by the Sphinx autosummary extension.

        {fullbasename}
        {bar}

        .. Documentation string which may be at the top of the module.
        .. automodule:: {name}
           :no-members:
           :no-inherited-members:

        .. currentmodule:: {name}

        .. Links to members.
        .. autosummary::
           :toctree:

        {members}
        """
        )

        # source/docpath/genname.rst
        self.doc_templ = textwrap.dedent(
            """
        .. rst file to pull only module doc strings at the top of the module
        .. file. These usually contain short tutorial-like stuff about what can
        .. be done with the module's content.

        .. In older sphinx versions, we needed to create at least one heading
        .. in each module doc string such that sphinx picks it up. This doesn't
        .. seem to be the case any longer.

        .. We use automodule with :no-members: to render only the module doc
        .. string.

        {fullbasename}
        {bar}

        .. automodule:: {name}
           :no-members:
           :no-inherited-members:
        """
        )

        self.name = name
        self.source = source
        self.apipath = apipath
        self.docpath = docpath
        spl = self.name.split(".")
        self.pkgname = spl[0]
        self.basename = spl[-1]
        self.fullbasename = ".".join(spl[1:])
        self.bar = "=" * len(self.fullbasename)
        self.genname = "__sphinx_autodoc_module__" + self.name

        self.obj = importlib.import_module(name)
        assert inspect.ismodule(self.obj)
        self.sourcefile = inspect.getsourcefile(self.obj)
        self.members = [
            x[0]
            for x in inspect.getmembers(self.obj)
            if is_mod_member(x[0], x[1], self.name)
        ]
        self.has_doc = False
        if self.sourcefile is not None:
            with open(self.sourcefile) as fh:
                lines = fh.readlines()[:3]
            for ll in lines:
                if ll.startswith('"""'):
                    self.has_doc = True
                    break

    def write_api(self):
        """Write source/apipath/genname.rst"""
        txt = self.api_templ.format(
            members=format_names(self.members),
            fullbasename=self.fullbasename,
            name=self.name,
            bar=self.bar,
        )
        file_write(
            pj(self.source, self.apipath, self.genname) + ".rst", txt
        )

    def write_doc(self):
        """Write source/docpath/genname.rst"""
        if self.has_doc:
            txt = self.doc_templ.format(
                fullbasename=self.fullbasename, name=self.name, bar=self.bar
            )
            file_write(
                pj(self.source, self.docpath, self.genname) + ".rst", txt
            )


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
    for loader, name, ispkg in pkgutil.iter_modules(
        pkg.__path__, prefix=pkg.__name__ + "."
    ):
        if ispkg:
            mod_names = walk_package(
                importlib.import_module(name), mod_names=mod_names
            )
        else:
            mod_names.append(name)
    return mod_names


def main():
    # source/apipath/index.rst
    api_index_templ = textwrap.dedent(
        """
    .. generated API doc index file

    API Reference
    -------------

    .. toctree::
       :maxdepth: 1

    {modules_api}
    """
    )

    # source/docpath/index.rst
    doc_index_templ = textwrap.dedent(
        """
    .. doc strings from modules index file

    Documentation from modules
    --------------------------

    .. toctree::
       :maxdepth: 3

    {modules_doc}
    """
    )

    written_index_templ = textwrap.dedent(
        """
    .. index for hand-written docu. Anything below {writtenpath}/ will not be
    .. overwritten, here you can place hand-written rst files, and list them
    .. in {writtenpath}/index.rst

    More Topics
    -----------

    .. toctree::
       :maxdepth: 1

       {writtenpath}/index
    """
    )

    # source/index.rst
    index_templ = textwrap.dedent(
        """
    {package_name}
    {bar}

    Table of contents
    -----------------
    .. toctree::
       :maxdepth: 1

       {apipath}/index
       __docpath_index_entry__
    """
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "package", help="The name of the package to walk (e.g. 'scipy')"
    )

    parser.add_argument(
        "-s",
        "--source",
        action="store",
        help="""sphinx source dir below which all rst files will
                be written [%(default)s]""",
        default="source",
    )
    parser.add_argument(
        "-a",
        "--apipath",
        action="store",
        help="""dir (relative to SOURCE) for generated API rst
                files, written by default, may be
                turned off by --no-write-api [%(default)s]""",
        default="generated/api",
    )
    parser.add_argument(
        "-d",
        "--docpath",
        action="store",
        help="""dir (relative to SOURCE) for extra generated rst
                files for doc strings pulled from modules, use with
                --write-doc, off by default [%(default)s]""",
        default="generated/doc",
    )
    parser.add_argument(
        "-w",
        "--writtenpath",
        action="store",
        help="""dir (relative to SOURCE) with hand written rst
                files, an index.rst file must exist there, this will be added
                to SOURCE/index.rst if found, only needed
                with --write-index [%(default)s]""",
        default="written",
    )
    parser.add_argument(
        "-i",
        "--write-index",
        action="store_true",
        help="""(over)write SOURCE/index.rst (a backup is made), not written by
                default""",
        default=False,
    )
    parser.add_argument(
        "--write-doc",
        action="store_true",
        help="""(over)write SOURCE/DOCPATH""",
        default=False,
    )
    parser.add_argument(
        "--no-write-api",
        action="store_false",
        dest="write_api",
        help="""don't (over)write SOURCE/APIPATH""",
        default=True,
    )
    parser.add_argument(
        "-X",
        "--exclude",
        help="""regex for excluding modules, applied to the full
                module name [%(default)s]""",
        default=None,
    )

    args = parser.parse_args()

    package_name = args.package
    bar = "=" * len(package_name)

    print(f"processing package: {package_name}")
    package = importlib.import_module(package_name)

    if args.exclude is not None:
        rex = re.compile(args.exclude)
        mod_filter = lambda name: rex.search(name) is None
    else:
        mod_filter = lambda name: True

    mods = [
        Module(
            name,
            source=args.source,
            apipath=args.apipath,
            docpath=args.docpath,
        )
        for name in walk_package(package) if mod_filter(name)
    ]

    modules_api = ""
    modules_doc = ""

    if args.write_api:
        os.makedirs(pj(args.source, args.apipath), exist_ok=True)
    if args.write_doc:
        os.makedirs(pj(args.source, args.docpath), exist_ok=True)

    print("modules:")
    for mod in mods:
        print(f"  {mod.name}")
        if args.write_api:
            mod.write_api()
            modules_api += format_name(mod.genname) + "\n"
        if args.write_doc and mod.has_doc:
            mod.write_doc()
            modules_doc += format_name(mod.genname) + "\n"

    if args.write_api:
        txt = api_index_templ.format(modules_api=modules_api)
        file_write(pj(args.source, args.apipath, "index.rst"), txt)

    if args.write_doc:
        txt = doc_index_templ.format(modules_doc=modules_doc)
        file_write(pj(args.source, args.docpath, "index.rst"), txt)
        index_templ = re.sub(
            "__docpath_index_entry__", "{docpath}/index", index_templ
        )
    else:
        index_templ = re.sub("__docpath_index_entry__", "", index_templ)

    if args.write_index:
        index_fn = pj(args.source, "index.rst")
        w_pth = pj(args.source, args.writtenpath)
        w_index_fn = pj(w_pth, "index.rst")
        print(f"overwriting main index: {index_fn}")
        if os.path.exists(w_pth):
            assert os.path.exists(w_index_fn), (
                f"trying to write {index_fn}: {w_pth} exists "
                f"but {w_index_fn} not found"
            )
            index_templ += written_index_templ
        txt = index_templ.format(
            apipath=args.apipath,
            docpath=args.docpath,
            writtenpath=args.writtenpath,
            package_name=package_name,
            bar=bar,
        )
        file_write(index_fn, txt, backup=True)
