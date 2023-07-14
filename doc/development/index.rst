.. _section_development:

Development
===========

This section of the documentation is mostly aimed at people who would like to contribute to the development of `cotainr`.

The `cotainr` source code is version controlled using `git <https://git-scm.com/>`_ and is hosted on GitHub: https://github.com/DeiC-HPC/cotainr

The :ref:`reference documentation <reference_docs>` is hosted on Read the Docs: http://cotainr.readthedocs.io

Contributing to `cotainr`
-------------------------

All contributions, including bug reports, bug fixes, documentation, and new features are welcome.

`cotainr` is free and open source software licensed under the `European Union Public License (EUPL) 1.2 <https://joinup.ec.europa.eu/collection/eupl/introduction-eupl-licence>`_. See the `LICENSE <https://github.com/DeiC-HPC/cotainr/blob/main/LICENSE>`_ file for details about your rights and obligations when using and contributing to `cotainr`.

Feedback & bug reports
~~~~~~~~~~~~~~~~~~~~~~
If you would like to report a bug, request a new features, or provide feedback and/or ideas for improving `cotainr`, please create an issue on the `cotainr` issue tracker: https://github.com/DeiC-HPC/cotainr/issues. A guide for creating an issue on GitHub is available in the `GitHub issue docs <https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue>`_. Before creating a new issue, please check if somebody else has already opened a similar issue. If so, please contribute your thoughts and experiences to the discussion in that issue instead of opening a new one. If reporting a bug, please provide a `minimal reproducible example <https://stackoverflow.com/help/minimal-reproducible-example>`_ of the problem.

Code & documentation contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you would like to contribute changes to the `cotainr` codebase or documentation, you are welcome to create a pull request towards the *main* branch on the `cotainr` GitHub repo: https://github.com/DeiC-HPC/cotainr. A guide for creating a pull request is available in the `GitHub pull request docs <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_. Please familiarize yourself with the :ref:`style guide <style_guide>`, :ref:`test suite <test_suite>`, and :ref:`reference documentation <reference_docs>` before creating a pull request. Your pull request is much more likely to be accepted and merged into `cotainr` if it follows the style guidelines for `cotainr`, includes proper tests, and is documented. Also, please keep pull request to a single topic.

..
    Toc for the rest of the development pages
.. toctree::
    :maxdepth: 1
    :hidden:

    style_guide
    test_suite_ci_cd
    documentation
    technical_motivation
    cli_internals
    tracing_logging
    releasing
    systems
