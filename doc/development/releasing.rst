.. _releasing:

Releasing a new version
=======================

Most of the process related to releasing a new version of `cotainr` is automated. However a few things, as detailed on this page, must still be done to initiate the release process.

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

Release process
---------------
In order to release a new version of `cotainr`, one must:

1. Create a new branch with release notes in the format `YYYY.MM.MINOR.md` in the folder `doc/release_notes` based on the template `doc/release_notes/release_note.md.template`.
2. Assert succesful :ref:`CI tests <continuous_integration>` and merge the release notes into the main branch.
3. Tag the main branch locally as `git tag YYYY.MM.MINOR`
4. Push the tag to the GitHub repository `git push origin tag YYYY.MM.MINOR`. This launches the :ref:`CD setup <continuous_delivery>` GitHub action.
5. Review the `CI on release` GitHub action and approve the TestPyPI and PyPI deployment if succesful.
