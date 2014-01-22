Description
===========

The script ``sphinx-autodoc.py`` is similar to ``sphinx-apidoc`` provided with
Sphinx. It walkes thru a Python package and generates rst files for

* full API doc (each module will be treated by ``autosummary``)
* doc strings from modules
* detect and include hand written docu

Using it is a 2-step process. First, run Sphinx' own ``sphinx-quickstart`` to
set up a sphinx project, then ``sphinx-autodoc.py`` to generate all rst files .


Usage
=====

Set up doc dir using ``sphinx-quickstart``
------------------------------------------

Create a sphinx doc dir for your project (lets assume ``myproject/doc`` with
the source dir ``myproject/doc/source`` and the main index file
``myproject/source/doc/index.rst``)::
    
    $ cd myproject
    $ sphinx-quickstart

Choose a separate source and build dir (e.g. ``doc/source`` and ``doc/build``).
Accept most other defaults. Especially, say yes to the "autodoc" extension.

Modify ``doc/source/conf.py`` to include these lines::

    autodoc_default_flags = ['members', 'show-inheritance', 'special-members']
    ##autodoc_default_flags = ['members']

    autosummary_generate = True

You may play with ``autodoc_default_flags``, but the important part is
``autosummary_generate``.


Use sphinx-autodoc.py
---------------------

Now walk thru the package and create rst files. We use ``-i`` to create
an initial ``source/index.rst``::

    $ sphinx-autodoc.py -i -s doc/source myproject

Note that this will overwrite an existing ``index.rst`` file (a backup is made
however).

You can run the script from anywhere (no need to cd to the project dir). Only
the source path ``-s`` must point to the dir where you want all rst files to 
be generated.

Now modify ``source/index.rst`` to suit you needs and then run ``make html``
using the Sphinx-generated Makefile. Then watch the docu::

    $ firefox -new-window build/html/index.html &


Notes for numpydoc
==================

If you want to use numpydoc and the numpy doc string format, then do this:

Grab a copy of numpydoc. Note that you could install that as a separate
package, but this was not tested so far. We add the numpydoc files to the doc
source ``myproject/doc/`` ::
    
    ($ aptitude install python-setuptools)
    $ mkdir myproject/doc/source/sphinxext
    $ cd /tmp
    $ easy_install --prefix doc numpydoc
    $ cp -r doc/lib/python2.7/site-packages/numpydoc-0.4-py2.7.egg/numpydoc \
      /path/to/myproject/doc/source/sphinxext/

Modify ``doc/source/conf.py`` to include numpydoc::

    sys.path.insert(0, os.path.abspath('sphinxext'))
    extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage',
                  'sphinx.ext.viewcode', 'sphinx.ext.autosummary',
                  'numpydoc']

Next, grab a recent copy of numpy and copy the ``class.rst`` file::

    $ git clone ...
    $ mkdir -p doc/source/_templates/autosummary
    $ cp numpy/doc/source/_templates/autosummary/class.rst doc/source/_templates/autosummary/ 

