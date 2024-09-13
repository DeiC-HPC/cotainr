"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

from cotainr.cli import _extract_help_from_docstring


class TestExtractHelpFromDocstring:
    def test_arg_not_found(self):
        docstring = """
            Summary

            Parameters
            ----------
            foo : str
                Foo

            Returns
            -------
            bar : str
                Bar
            """
        with pytest.raises(
            KeyError, match="The docstring does not include arg='some_arg'"
        ):
            _extract_help_from_docstring(arg="some_arg", docstring=docstring)

    def test_description_first_letter_lower_case(self):
        docstring = """
        Parameters
        ----------
        some_arg : int
            The INTEGER
        """
        help_msg = _extract_help_from_docstring(arg="some_arg", docstring=docstring)
        assert help_msg == "the INTEGER"

    def test_description_period_strip(self):
        docstring = """
        Parameters
        ----------
        some_arg : float
            A float.
        """
        help_msg = _extract_help_from_docstring(arg="some_arg", docstring=docstring)
        assert help_msg == "a float"

    def test_description_whitespace_strip(self):
        docstring = """
        Parameters
        ----------
        some_arg : str
            Much leading and trailing space
        """
        # Doctor the docstring a little here, so editors etc. which eagerly
        # strip whitespace don't mess up the test.
        docstring = docstring.replace("space", "space" + " " * 10)
        help_msg = _extract_help_from_docstring(arg="some_arg", docstring=docstring)
        assert help_msg == "much leading and trailing space"

    def test_multi_line_arg_description(self):
        docstring = """
        Parameters
        ----------
        some_arg : list
            Some description of this list
            on multiple lines
        """
        help_msg = _extract_help_from_docstring(arg="some_arg", docstring=docstring)
        assert help_msg == "some description of this list on multiple lines"

    def test_no_param_section(self):
        docstring = """No args here..."""
        with pytest.raises(
            KeyError, match="The docstring does not include arg='some_arg'"
        ):
            _extract_help_from_docstring(arg="some_arg", docstring=docstring)

    def test_single_line_arg_description(self):
        docstring = """
        Parameters
        ----------
        some_arg : tuple
            Some description of this tuple on one line.

        Returns
        -------
        something : None
            Not really anything...
        """
        help_msg = _extract_help_from_docstring(arg="some_arg", docstring=docstring)
        assert help_msg == "some description of this tuple on one line"
