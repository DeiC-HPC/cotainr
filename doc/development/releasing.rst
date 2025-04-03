.. _releasing:

Releasing a new version
=======================

Most of the process related to releasing a new version of `cotainr` is automated. However a few things, as detailed on this page, must still be done to initiate the release process.

Release process
---------------
In order to release a new version of `cotainr`, one must:

1. Create a new branch and run the `doc/prepare_release.py` script to update the docs version switcher and create a release notes skeleton.
2. Fill in the release notes in the created `YYYY.MM.MICRO.md` release notes skeleton file in the `doc/release_notes` folder.
3. Open a new pull request to merge the release notes and the updated docs version switcher into main and assert successful :ref:`CI tests <continuous_integration>` of the branch. Then merge it into the main branch.
4. Tag the main branch locally using :code:`git tag YYYY.MM.MICRO` and push the tag to the GitHub repository :code:`git push origin tag YYYY.MM.MICRO`. This triggers the :ref:`CD on release <continuous_integration>` GitHub action.
5. Review and verify that :ref:`CD on release <continuous_integration>` creates a GitHub release. Then review and approve the TestPyPI and PyPI deployments. Finally review that `readthedocs` is updated correctly, i.e. assert that the `stable <https://cotainr.readthedocs.io/en/stable>`_ and `latest <https://cotainr.readthedocs.io/en/latest>`_ docs versions points to the newly released version.

.. _version-scheme:

Versioning scheme
-----------------
A `CalVer <https://calver.org/>`_ versioning scheme is used for `cotainr`, more specifically:

.. code-block:: text

  YYYY.MM.MICRO

with:

- :code:`YYYY` - full year - 2022, 2023, ...
- :code:`0M` - zero-padded month - 1, 2 ... 11, 12
- :code:`MICRO` - zero-indexed counter specific to :code:`YYYY.MM` - 0, 1, ... - incremented for each version released in a given year/month.


Version single-sourcing
-----------------------
The cotainr version (in code and docs) is single-sourced using the logic in the :mod:`cotainr._version` module. The version number is generated according to the following logic:

1. If the cotainr git history is available and the `hatch-vcs package <https://pypi.org/project/hatch-vcs/>`_ is installed, the version number is generated from the latest `YYYY.MM.MICRO` release tag in the git history.

   - If additional commits since the latest release tag are present in the git history, the version number is suffixed with a `.dev<N>+g<commit_sha>` string, where `<N>` is the number of commits since the latest release tag and `<commit_sha>` is the short hash of the latest commit in the git history.
   - If uncommitted changes are present in the working directory, the version number is further suffixed with a `.d<YYYYMMDD>` string, where `<YYYYMMDD>` is the current date.

2. If the cotainr git history is not available, but cotainr wheel/sdist package metadata is available, i.e., cotainr is installed from a wheel, the `YYYY.MM.MICRO` version number is read from the package metadata.
3. If the cotainr git history is not available and no cotainr package metadata is available, the version number is reported as `"<unknown version>"`.

When building the cotainr wheel/sdist packages, the version number is automatically extracted using the `hatch-vcs package <https://pypi.org/project/hatch-vcs/>`_.

When running the `prepare_release.py` script, the version number is automatically created based on the specified release date (or the current date, if not release date is specified) and the latest release tag in the git history.
