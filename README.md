About
=====

`sphinx-autodoc` is almost, but not quite, entirely unlike `sphinx-apidoc` and
`sphinx-autogen` provided with Sphinx. It is a tool to automatically
create `.rst` source files, from which Sphinx can create API
documentation.

It does this by walking thru a Python package and generating rst files
for:

* Full API doc. Each module will be treated by the [autosummary]
  extension `sphinx.ext.autosummary`. Files are written to
  `source/generated/api` by default. Module doc strings (if present) are also
  included.
* Detect and include hand written docs, by default in `source/written/`.

Install
=======

```sh
$ git clone ...
$ cd sphinx-autodoc
$ pip install [-e] .
```

Usage tl;dr
===========

```sh
$ cd myproject/doc
$ sphinx-autodoc myproject
$ make html
$ firefox build/html/index.html
```

Examples
========

We provide a minimal, self-contained Python package with a doc dir for
experimentation: `example_package/autodoctest`. In particular, check out
`example_package/autodoctest/doc/generate-apidoc.sh`.

```sh
$ cd example_package/autodoctest/
$ pip install -e .
$ cd doc
$ ./generate-apidoc.sh
$ firefox build/html/index.html
```

Usage
=====

Set up doc dir using `sphinx-quickstart`
----------------------------------------

If you haven't already, create a sphinx doc dir for your project (lets assume
`myproject/doc` with the source dir `myproject/doc/source` and the main index
file `myproject/doc/source/index.rst`).

```sh
$ cd myproject/doc
$ sphinx-quickstart
```

Choose a separate source and build dir (e.g. `doc/source` and
`doc/build`). Accept most other defaults.

Configuration
-------------

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


Notes for numpydoc, class template
----------------------------------

We used to use [numpydoc] and numpy's class template in the past. However, with
recent Sphinx versions, the [napoleon] extension does a great job. Use our own
class template if you like in conjunction with that: copy
`example_package/autodoctest/doc/source/_templates/autosummary/class.rst` to
your `doc/source/_templates/autosummary/`.

Use sphinx-autodoc
------------------

tl;dr: See `example_package/autodoctest/doc/generate-apidoc.sh`


Now walk thru the package and create rst files. We use `-i` to create an
initial `source/index.rst`.

```sh
$ sphinx-autodoc -i -s doc/source myproject
```

Note that this will overwrite an existing `index.rst` file (a backup is
made however).

You can run the script from anywhere, provided that `myproject` is a
Python package since we need to import it to inspect all its subpackages
and modules. The source path `-s` must point to the dir where you want
all rst files to be generated, which will usually be `doc/source/`.

Now modify `source/index.rst` to suit you needs and then run `make html`
using the Makefile generated by `sphinx-quickstart` earlier. Inspect the
rendered docs.

```sh
$ firefox build/html/index.html
```

[numpydoc]: https://numpydoc.readthedocs.io
[napoleon]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[autosummary]: https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
