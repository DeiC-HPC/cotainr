.. _releasing:

Releasing a new version
=======================

Most of the process related to releasing a new version of `cotainr` is automated. However a few things, as detailed on this page, must still be done to initiate the release process.

Release process
---------------
In order to release a new version of `cotainr`, one must:

1. Update the :attr:`cotainr.__version__` string in `cotainr/__init__.py`.
2. Update the docs version switcher list by running the `doc/create_switcher.py` script.
3. Create a new branch and create new release notes in the format `YYYY.MM.MINOR.md` in the folder `doc/release_notes` based on the template `doc/release_notes/release_note.md.template` and fill in the release notes.
4. Open a new pull request to merge the release notes into main and assert successful :ref:`CI tests <continuous_integration>` of the branch. Then merge it into the main branch.
5. Tag the main branch locally using :code:`git tag YYYY.MM.MINOR` and push the tag to the GitHub repository :code:`git push origin tag YYYY.MM.MINOR`. This triggers the :ref:`CD on release <continuous_integration>` GitHub action.
6. Review and verify that :ref:`CD on release <continuous_integration>` creates a GitHub release. Then review and approve the TestPyPI and PyPI deployments. Finally review that `readthedocs` is updated correctly, i.e. assert that the `stable <https://cotainr.readthedocs.io/en/stable>`_ and `latest <https://cotainr.readthedocs.io/en/latest>`_ docs versions points to the newly released version.

.. _version-scheme:

Versioning scheme
-----------------
A `CalVer <https://calver.org/>`_ versioning scheme is used for `cotainr`, more specifically:

.. code-block:: text

  YYYY.MM.MINOR

with:

- :code:`YYYY` - full year - 2022, 2023, ...
- :code:`MM` - short month - 1, 2 ... 11, 12
- :code:`MINOR` - zero-indexed counter specific to :code:`YYYY.MM` - 0, 1, ... - incremented for each version released in a given year/month.
