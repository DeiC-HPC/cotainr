.. _reference_docs:

Building the reference docs
===========================

Dependencies

.. include:: ../../docs-requirements.txt
    :literal:

Acknowledgements
----------------
NumPy/SciPy/Pandas documentation design


## Documentation

The `cotainr` documentation is included in the "doc" folder as restructured text files. An HTML version of the documentation may be rendered using the Sphinx configuration included in the "doc" folder. Simply run the following commands from the "doc" folder:

```bash
$ make apidoc
$ make relnotes
$ make html
```

The `make apidoc` command generates restructured text files for the API reference documentation. These files include `sphinx.ext.autodoc` directives that automatically generates the API reference documentation from the docstrings of the modules/classes/functions/... in `cotainr`. The `make relnotes` command generates the list of release notes from the markdown files in the `doc/release_notes` folder.

