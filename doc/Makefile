# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SOURCEDIR     = .
BUILDDIR      = _build
PACKAGENAME   = cotainr

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@python3 -c """import sphinx.util; print('  %s  to autogenerate the API reference rst files' % sphinx.util.console.blue('apidoc'.ljust(10)))"""
	@python3 -c """import sphinx.util; print('  %s  to autogenerate the release notes rst file' % sphinx.util.console.blue('relnotes'.ljust(10)))"""

.PHONY: help apidoc Makefile

apidoc:
	@$(SPHINXAPIDOC) --force --separate --no-toc -o api_reference $(SOURCEDIR)/../$(PACKAGENAME) $(SOURCEDIR)/../$(PACKAGENAME)/tests/*
	@echo "Removing file api_reference/cotainr.rst"
	@rm api_reference/cotainr.rst

relnotes:
	@python3 release_notes/create_release_notes_list.py

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
