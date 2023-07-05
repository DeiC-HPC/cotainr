.. _releasing:

Releasing a new version
=======================

Most of the process related to releasing a new version of `cotainr` is automated. However a few things, as detailed on this page, must still be done to initiate the release process.

Versioning scheme
-----------------
A `CalVer <https://calver.org/>`_ versioning scheme is used for `cotainr`, more specifically:

.. code-block:: text

  YYYY.MM.MINOR

with:

- :code:`YYYY` - full year - 2022, 2023, ...
- :code:`MM` - short month - 1, 2 ... 11, 12
- :code:`MINOR` - zero-indexed counter specific to :code:`YYYY.MM` - 0, 1, ... - incremented for each version released in a given year/month.

Release process
---------------
In order to release a new version of `cotainr`, one must:

1. Update the :attr:`cotainr.__version__` string in `cotianr/__init__.py`.
2. Update the version switcher list by running the `create_switcher.py` script.
3. Create the associated release notes, i.e. create a `YYYY.MM.MINOR.md` file in the `doc/release_notes` folder based on the template `doc/release_notes/release_note.md.template`.
4. Update the project README.md with new version in EasyBuild script
5. Create a git tag (:code:`git tag YYYY.MM.MINOR`) for the version on the *main* branch and push it to the GitHub repository.
6. Assert that the :ref:`CD setup <continuous_delivery>` finishes correctly.
