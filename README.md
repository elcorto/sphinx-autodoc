# About

`sphinx-autodoc` is almost, but not quite, entirely unlike `sphinx-apidoc`
provided with Sphinx. It is a tool to automatically create `rst` source files,
from which Sphinx can create API documentation, which means you can build API
docs in a fully automatic way without having to write a single `rst` file by hand.

This tool was created when `sphinx-apidoc` wasn't really around yet and later
we never got it to work the way we wanted :) More on the differences between
the two tools below.

# Features

* Full API doc. Each module will be treated by the
  [`sphinx.ext.autosummary`][autosummary] extension. Files are written to
  `source/generated/api` by default. Module doc strings (if present) are also
  included. Every module member (class, function) is documented on a separate
  page.
* Optionally (`-i/--write-index`) create an initial `index.rst`. Reference hand
  written docs (by default in `source/written/`) in there.
* Optionally (`--write-doc`), pull module doc strings into a separate dir
  (`source/doc/`) and also reference them in `source/index.rst` (if
  `--write-index`).
* `class.rst` template file (details below). Has been tested on numpy-ish code
  bases using the numpy docstring format. It works well in conjunction with the
  defaults that we implement and the recommended settings in Sphinx' `conf.py`.

API docs generated with `sphinx-autodoc` can be found [here][imagecluster],
[here][pwtools] or [here][psweep].


# Install

```sh
$ git clone ...
$ cd sphinx-autodoc
$ pip install [-e] .
```

# Usage tl;dr

```sh
$ cd myproject/doc
$ sphinx-autodoc myproject

# Sphinx
$ make html
$ firefox build/html/index.html

# jupyterbook
##$ jb build source
##$ firefox source/_build/html/index.html
```

# Options

```
usage: sphinx-autodoc [-h] [-s SOURCE] [-a APIPATH] [-d DOCPATH]
                      [-w WRITTENPATH] [-i] [--write-doc] [--no-write-api]
                      [-X EXCLUDE]
                      package

positional arguments:
  package               The name of the package to walk (e.g. 'scipy')

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        sphinx source dir below which all rst files will be
                        written [source]
  -a APIPATH, --apipath APIPATH
                        dir (relative to SOURCE) for generated API rst files,
                        written by default, may be turned off by --no-write-
                        api [generated/api]
  -d DOCPATH, --docpath DOCPATH
                        dir (relative to SOURCE) for extra generated rst files
                        with module doc strings in addition to having them in
                        the API docs, use with --write-doc, off by default
                        [generated/doc]
  -w WRITTENPATH, --writtenpath WRITTENPATH
                        dir (relative to SOURCE) with hand written rst files,
                        an index.rst file must exist there, this will be added
                        to SOURCE/index.rst if found, only needed with
                        --write-index [written]
  -i, --write-index     (over)write SOURCE/index.rst (a backup is made), not
                        written by default
  --write-doc           (over)write SOURCE/DOCPATH
  --no-write-api        don't (over)write SOURCE/APIPATH
  -X EXCLUDE, --exclude EXCLUDE
                        regex for excluding modules, applied to the full
                        module name [None]
```

# Examples

We provide a minimal, self-contained Python package with a doc dir for
experimentation: `example_package/autodoctest`. In particular, check out
`example_package/autodoctest/doc/generate-doc.sh`. This implements a common
workflow: clean up old builds, call `sphinx-autodoc`, `make html`. Use this to
purge and re-build all your docs.

```sh
$ cd example_package/autodoctest/
$ pip install -e .
$ cd doc
$ ./generate-doc.sh
$ firefox build/html/index.html
```

# Usage

## With [`jupyterbook`][jupyterbook]

We recently started using jupyterbook instead of Sphinx directly and also
played with the new `:recursive:` option of `sphinx.ext.autosummary`. Still
API docs for each member end up on a single page. There [are ways to get
around this by fiddling with
templates](https://jupyterbook.org/en/stable/advanced/developers.html) but we
ended up using `sphinx-autodoc` to generate API docs and pointing
jupyterbook to the `generated/api/index.rst` file in `source/_toc.yml` was all
we needed.

Also we don't use `_templates/autosummary/class.rst`. Things still render
fine, so this template may be obsolete.

Check [this](https://github.com/elcorto/psweep/tree/main/doc) for how we use
it, with only minor modifications to `generate-doc.sh`.

## With Sphinx

### Set up a doc dir using `sphinx-quickstart`

If you haven't already, create a sphinx doc dir for your project (lets assume
`myproject/doc` with the source dir `myproject/doc/source` and the main index
file `myproject/doc/source/index.rst`).

```sh
$ cd myproject/doc
$ sphinx-quickstart
```

Choose a separate source and build dir (e.g. `doc/source` and
`doc/build`). Accept most other defaults.


### Configuration

Inspect `doc/source/conf.py` and make sure you have at least these
extensions enabled.

```py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    ]
```

We use the [napoleon] extension instead of [numpydoc]. See
`example_package/autodoctest/doc/source/conf.py` for more extensions.

Now modify `doc/source/conf.py` to include these configs.

```py
autosummary_generate = True

autodoc_default_options = {
    'members': True,
    # The ones below should be optional but work nicely together with
    # example_package/autodoctest/doc/source/_templates/autosummary/class.rst
    # and other defaults in sphinx-autodoc.
    'show-inheritance': True,
    'inherited-members': True,
    'no-special-members': True,
}
```

See also `example_package/autodoctest/doc/source/conf.py`.


### Notes for numpydoc, class template

We used to use [numpydoc] and numpy's class template in the past. However, with
recent Sphinx versions, the [napoleon] extension does a great job. Use our own
class template if you like in conjunction with that: copy
`example_package/autodoctest/doc/source/_templates/autosummary/class.rst` to
your `doc/source/_templates/autosummary/`.


### Use sphinx-autodoc

tl;dr: See `example_package/autodoctest/doc/generate-doc.sh`


Now walk through the package and create `rst` files. We use `-i` to create an
initial `source/index.rst`.

```sh
$ sphinx-autodoc -i -s doc/source myproject
```

Note that this will overwrite an existing `index.rst` file (a backup is
made however).

You can run the script from anywhere, provided that `myproject` is a
Python package since we need to import it to inspect all its subpackages
and modules. The source path `-s` must point to the dir where you want
all `rst` files to be generated, which will usually be `doc/source/`.

Now modify `source/index.rst` to suit you needs and then run `make html`
using the Makefile generated by `sphinx-quickstart` earlier. Inspect the
rendered docs.

```sh
$ firefox build/html/index.html
```

# Difference to `sphinx-apidoc`

The first difference is that `sphinx-apidoc` gets pointed to
a *source tree*.

```sh
$ cd myproject/doc
$ sphinx-apidoc -o source/generated/api ../src/myproject/
```

You may need to fuzz around with `sys.path` in `conf.py` such that Sphinx finds
your code since the `autodoc` extension needs to import each sub-package and
module anyway.

For this reason, we require your project to be installed and importable (which
is easy and safe with `pip install [--no-deps] -e .`). The argument to
`sphinx-autodoc` is thus the package *name*.

```sh
$ cd myproject/doc
$ sphinx-autodoc myproject
```

In fact you can run it from anywhere, but inside `myproject/doc` all defaults
(`-s source`, `-a generated/api`) work.

The second difference is what we put into generated module stub files. Examples
of generated files using the `example_package/autodoctest` package are listed
below.

`sphinx-apidoc` generates a `automodule` directive only, which will make all
docs for the module end up on a single page. We automatically create
`autosummary` directives and list all module members. This makes Sphinx create
one page per member. We have found no way to do the same with Sphinx' own
tools. If there is, ping me or send a PR against this file.

## `sphinx-apidoc`

```rst
main module
===========

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:
```

## `sphinx-autodoc`

```rst
.. rst file which lists all members of the current module. They will be
.. handled by the Sphinx autosummary extension.

main
====

.. Documentation string which may be at the top of the module.
.. automodule:: autodoctest.main
   :no-members:
   :no-inherited-members:

.. currentmodule:: autodoctest.main

.. Links to members.
.. autosummary::
   :toctree:

   Bar
   Baz
   Foo
   func
```


[numpydoc]: https://numpydoc.readthedocs.io
[napoleon]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[autosummary]: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
[imagecluster]: https://elcorto.github.io/imagecluster/generated/api/
[pwtools]: https://elcorto.github.io/pwtools/generated/api/
[psweep]: https://github.com/elcorto/psweep
[jupyterbook]: https://jupyterbook.org
