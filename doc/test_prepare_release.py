"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import datetime
import inspect
import locale
from subprocess import CompletedProcess

import pytest

from .prepare_release import _format_date, create_docs_switcher, create_release_notes


@pytest.fixture
def set_DK_locale():
    current_locale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, "da_DK.UTF-8")
    yield
    locale.setlocale(locale.LC_TIME, current_locale)


@pytest.fixture
def capture_file_write_text(monkeypatch):
    captured_text = []

    def mock_write_text(self, data, encoding=None, errors=None, newline=None):
        captured_text.append(data)

    monkeypatch.setattr("pathlib.Path.write_text", mock_write_text)
    return captured_text


class Test_create_docs_switcher:
    def test_correctly_formatted_switcher(self, monkeypatch, capture_file_write_text):
        def mock_subprocess_run(*args, **kwargs):
            return CompletedProcess(
                args="", returncode=0, stdout="2023.01.0\n2023.02.0\n2023.11.0\n"
            )

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)

        create_docs_switcher(new_release_ver="2025.01.0")
        expected_switcher = inspect.cleandoc(  # Remove leading whitespace
            """
            [
              {
                "name": "dev",
                "version": "latest",
                "url": "https://cotainr.readthedocs.io/en/latest/"
              },
              {
                "name": "2025.01.0 (stable)",
                "version": "stable",
                "url": "https://cotainr.readthedocs.io/en/stable/"
              },
              {
                "name": "2023.11.0",
                "version": "2023.11.0",
                "url": "https://cotainr.readthedocs.io/en/2023.11.0/"
              },
              {
                "name": "2023.02.0",
                "version": "2023.02.0",
                "url": "https://cotainr.readthedocs.io/en/2023.02.0/"
              },
              {
                "name": "2023.01.0",
                "version": "2023.01.0",
                "url": "https://cotainr.readthedocs.io/en/2023.01.0/"
              }
            ]
            """
        )
        assert len(capture_file_write_text) == 1  # Only one file written
        assert capture_file_write_text[0] == expected_switcher

    @pytest.mark.parametrize(
        "invalid_version_number", ["2025.1.0", "1900.02.0", "2025.32.1", "2025.02.01"]
    )
    def test_invalid_version_number(
        self, invalid_version_number, capture_file_write_text
    ):
        with pytest.raises(AssertionError):
            create_docs_switcher(
                new_release_ver=invalid_version_number,
            )


class Test_create_release_notes:
    def test_correctly_formatted_output(self, capture_file_write_text):
        create_release_notes(
            new_release_ver="2025.01.0", release_date=datetime.date(2025, 1, 1)
        )
        expected_release_notes = (
            inspect.cleandoc(  # Remove leading whitespace
                """
            # 2025.01.0

            **Released on January 1st, 2025**

            [Documentation for this release](https://cotainr.readthedocs.org/en/2025.01.0/)

            __short summary__

            ## New features

            - __new feature (externals) description__, __link to GitHub PR__

            ## Bug fixes

            - __bug fix description__, __link to GitHub PR__

            ## Maintenance updates

            - __maintenance update (internals) description__, __link to GitHub PR__
            """
            )
            + "\n"  # Newline at the end of the file
        )
        assert len(capture_file_write_text) == 1  # Only one file written
        assert capture_file_write_text[0] == expected_release_notes

    @pytest.mark.parametrize(
        "invalid_version_number", ["2025.1.0", "1900.02.0", "2025.32.1", "2025.02.01"]
    )
    def test_invalid_version_number(
        self, invalid_version_number, capture_file_write_text
    ):
        with pytest.raises(AssertionError):
            create_release_notes(
                new_release_ver=invalid_version_number,
                release_date=datetime.date(2025, 1, 1),
            )


@pytest.mark.parametrize(
    ["iso_input", "formatted_date"],
    [
        ("2021-01-01", "January 1st, 2021"),
        ("2021-01-02", "January 2nd, 2021"),
        ("2021-01-03", "January 3rd, 2021"),
        ("2022-02-04", "February 4th, 2022"),
        ("2022-02-05", "February 5th, 2022"),
        ("2022-02-06", "February 6th, 2022"),
        ("2023-03-07", "March 7th, 2023"),
        ("2023-03-08", "March 8th, 2023"),
        ("2023-03-09", "March 9th, 2023"),
        ("2023-03-10", "March 10th, 2023"),
        ("2024-04-11", "April 11th, 2024"),
        ("2024-04-12", "April 12th, 2024"),
        ("2024-04-13", "April 13th, 2024"),
        ("2025-05-14", "May 14th, 2025"),
        ("2025-05-15", "May 15th, 2025"),
        ("2025-05-16", "May 16th, 2025"),
        ("2026-06-17", "June 17th, 2026"),
        ("2026-06-18", "June 18th, 2026"),
        ("2026-06-19", "June 19th, 2026"),
        ("2027-07-20", "July 20th, 2027"),
        ("2027-07-21", "July 21st, 2027"),
        ("2027-07-22", "July 22nd, 2027"),
        ("2028-08-23", "August 23rd, 2028"),
        ("2028-08-24", "August 24th, 2028"),
        ("2028-08-25", "August 25th, 2028"),
        ("2029-09-26", "September 26th, 2029"),
        ("2029-09-27", "September 27th, 2029"),
        ("2030-10-28", "October 28th, 2030"),
        ("2031-11-29", "November 29th, 2031"),
        ("2032-12-30", "December 30th, 2032"),
        ("2032-12-31", "December 31st, 2032"),
    ],
)
class Test_format_date:
    def test_date_formatting_default_locale(self, iso_input, formatted_date):
        assert _format_date(datetime.date.fromisoformat(iso_input)) == formatted_date

    def test_date_formatting_dk_locale(self, iso_input, formatted_date, set_DK_locale):
        assert locale.getlocale(locale.LC_TIME) == ("da_DK", "UTF-8")
        assert _format_date(datetime.date.fromisoformat(iso_input)) == formatted_date
