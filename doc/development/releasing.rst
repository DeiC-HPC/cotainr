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
2. Update the version switcher list by running the `doc/create_switcher.py` script.
3. Create the associated release notes, i.e. create a `YYYY.MM.MINOR.md` file in the `doc/release_notes` folder based on the template `doc/release_notes/release_note.md.template`.
4. Update the project README.md with new version in EasyBuild script (and possibly new `system.json` content).
5. When all of these changes have been merged into *main* branch create a git tag (:code:`git tag YYYY.MM.MINOR`) for the version on the *main* branch and push it to the GitHub repository.
6. Create a release on Github from the tag. Use the tag as release title and the release notes as description in MD-format.
7. Assert that the :ref:`CD setup <continuous_delivery>` finishes correctly by checking that `readthedocs` is updated correctly (fx. that `stable <https://cotainr.readthedocs.io/en/stable>`_ and `latest <https://cotainr.readthedocs.io/en/latest>`_ points to the latest version and that the version is available by itself as well). If the version does not show up all builds from Read the Docs can be found under `versions <https://readthedocs.org/projects/cotainr/versions/>`_.
