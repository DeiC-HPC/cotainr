.. _reference_docs:

Reference documentation
=======================

The `cotainr` reference documentation is what you are reading right now. It consists of a set of `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ files in the `doc` folder along with all the `docstrings <https://peps.python.org/pep-0257/>`_ in the `cotainr` Python source code, and the `markdown <https://commonmark.org/>`_ release notes in the `doc/release_notes` folder. All of it is tied together via a `Sphinx <https://www.sphinx-doc.org/en/master/>`_ setup for building an HTML version of the documentation which is hosted on http://cotainr.readthedocs.io.

.. _building_the_html_docs:

Building the HTML version
-------------------------
The HTML version of the documentation may be built by running the following commands from the `doc` folder:

.. code-block:: console

    $ make apidoc
    $ make relnotes
    $ make html

The HTML output is available in the `doc/_build` folder. The :code:`make apidoc` command generates reStructuredText files for the API reference documentation. These files include :code:`sphinx.ext.autodoc` directives that automatically generate the API reference documentation from the docstrings of the modules/classes/functions/... in `cotainr`. The :code:`make relnotes` command generates the list of release notes from the markdown files in the `doc/release_notes` folder.

The HTML version of the documentation is based on the `PyData Spinx Theme <https://pydata-sphinx-theme.readthedocs.io/>`_ and its design and layout is heavily inspired by the `NumPy <https://numpy.org/doc/stable/>`_, `SciPy <https://docs.scipy.org/doc/scipy/>`_, and `Pandas <https://pandas.pydata.org/docs>`_ documentations - a big shout-out to the people who created those documentation designs!

Dependencies
~~~~~~~~~~~~
In order to build the HTML version of the documentation, you must have the Python packages listed the `docs-requirements.txt <https://github.com/DeiC-HPC/cotainr/blob/main/docs-requirements.txt>`_ installed, i.e.

.. include:: ../../docs-requirements.txt
    :literal:

Also, in order to run the above :code:`make` commands, you muse have `make <https://www.gnu.org/software/make/>`_ installed.