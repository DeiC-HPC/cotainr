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

from .prepare_release import (
    _check_release_version_format,
    _format_release_notes_date,
    create_docs_switcher,
    create_release_notes,
    format_release_version_and_date,
)


class Test__check_release_version_format:
    def test_acceptable_YYYY_0M_MICRO_format(self):
        assert _check_release_version_format(release_version="2025.03.1")

    def test_unacceptable_YYYY_0M_MICRO_format(self):
        with pytest.raises(ValueError):
            _check_release_version_format(release_version="2025.04.0")

    @pytest.mark.parametrize(
        "valid_version_number", ["2023.12.0", "2025.1.0", "2025.2.0"]
    )
    def test_correct_YYYY_MM_MICRO_format(self, valid_version_number):
        assert _check_release_version_format(release_version=valid_version_number)

    @pytest.mark.parametrize(
        "invalid_version_number", ["1900.2.0", "2025.32.1", "2025.2.01"]
    )
    def test_wrong_format(self, invalid_version_number):
        with pytest.raises(ValueError):
            _check_release_version_format(release_version=invalid_version_number)

    def test_not_raising_error(self):
        assert not _check_release_version_format(
            release_version="1999.1.0", raise_error=False
        )


class Test_create_docs_switcher:
    def test_correctly_formatted_switcher(self, monkeypatch):
        def mock_subprocess_run(*args, **kwargs):
            return CompletedProcess(
                args="", returncode=0, stdout="2022.1.0\n2022.02.0\n2022.11.0\n"
            )

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)
        expected_switcher = inspect.cleandoc(  # Remove leading whitespace
            """
            [
              {
                "name": "dev",
                "version": "latest",
                "url": "https://cotainr.readthedocs.io/en/latest/"
              },
              {
                "name": "2025.1.0 (stable)",
                "version": "stable",
                "url": "https://cotainr.readthedocs.io/en/stable/"
              },
              {
                "name": "2022.11.0",
                "version": "2022.11.0",
                "url": "https://cotainr.readthedocs.io/en/2022.11.0/"
              },
              {
                "name": "2022.02.0",
                "version": "2022.02.0",
                "url": "https://cotainr.readthedocs.io/en/2022.02.0/"
              },
              {
                "name": "2022.1.0",
                "version": "2022.1.0",
                "url": "https://cotainr.readthedocs.io/en/2022.1.0/"
              }
            ]
            """
        )
        switcher = create_docs_switcher(formatted_release_version="2025.1.0")
        assert switcher == expected_switcher

    def test_invalid_version_number(self):
        with pytest.raises(ValueError):
            create_docs_switcher(formatted_release_version="hello 6021!")


class Test_create_release_notes:
    def test_correctly_formatted_output(self):
        expected_release_notes = (
            inspect.cleandoc(  # Remove leading whitespace
                """
            # 2025.1.0

            **Released on January 1st, 2025**

            [Documentation for this release](https://cotainr.readthedocs.org/en/2025.1.0/)

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
        release_notes = create_release_notes(
            formatted_release_version="2025.1.0",
            formatted_release_date="January 1st, 2025",
        )
        assert release_notes == expected_release_notes

    def test_invalid_version_number(self):
        with pytest.raises(ValueError):
            create_release_notes(
                formatted_release_version="hello 6021!",
                formatted_release_date="invalid date",
            )


class Test_format_release_version_and_date:
    def test_correctly_formatted_date(self, monkeypatch):
        monkeypatch.setattr("cotainr.__version__", "2025.03.0")
        _, formatted_release_date = format_release_version_and_date(
            release_date="2025-04-01"
        )
        assert formatted_release_date == "April 1st, 2025"

    @pytest.mark.parametrize(
        ["current_release_version", "release_date", "new_formatted_release_version"],
        [
            (
                "2025.1.1",
                "2025-01-15",
                "2025.1.1",
            ),  # would be automatically set to 2025.1.1 by hatch-vcs
            (
                "2025.1.2",
                "2025-01-16",
                "2025.1.2",
            ),  # would be automatically set to 2025.1.1 by hatch-vcs
            ("2025.1.2", "2025-03-17", "2025.3.0"),
            (
                "2025.12.3",
                "2025-12-22",
                "2025.12.3",
            ),  # would be automatically set to 2025.1.1 by hatch-vcs
            ("2025.12.3", "2026-01-23", "2026.1.0"),
            ("2025.1.0", "2026-11-20", "2026.11.0"),
        ],
    )
    def test_correctly_formatted_version(
        self,
        current_release_version,
        release_date,
        new_formatted_release_version,
        monkeypatch,
    ):
        monkeypatch.setattr("cotainr.__version__", current_release_version)
        formatted_release_version, _ = format_release_version_and_date(
            release_date=release_date
        )

        assert formatted_release_version == new_formatted_release_version

    @pytest.mark.parametrize(
        ["current_release_version", "release_date"],
        [
            ("2025.1.0", "2024-01-01"),
            ("2025.2.0", "2025-01-31"),
            ("2025.2.0", "2024-01-10"),
        ],
    )
    def test_invalid_release_date(
        self, current_release_version, release_date, monkeypatch
    ):
        monkeypatch.setattr("cotainr.__version__", current_release_version)
        with pytest.raises(
            ValueError,
            match=(
                f"New release date {release_date} is before the current version "
                f"{current_release_version}."
            ),
        ):
            format_release_version_and_date(release_date=release_date)

    def test_release_today(self, monkeypatch):
        class MockedDatetime(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2025, 10, 1)

        monkeypatch.setattr(datetime, "datetime", MockedDatetime)
        monkeypatch.setattr("cotainr.__version__", "2025.1.0")
        formatted_release_version, formatted_release_date = (
            format_release_version_and_date()
        )
        assert formatted_release_version == "2025.10.0"
        assert formatted_release_date == "October 1st, 2025"

    def test_unknown_current_version(self, monkeypatch):
        monkeypatch.setattr("cotainr.__version__", "<unknown version>")
        with pytest.raises(
            ValueError,
            match="Current release version <unknown version> is not in the expected format.",
        ):
            format_release_version_and_date(release_date="2025-01-01")


class Test_format_release_notes_date:
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
    def test_date_formatting_default_locale(self, iso_input, formatted_date):
        assert (
            _format_release_notes_date(datetime.date.fromisoformat(iso_input))
            == formatted_date
        )

    def test_error_on_dk_locale(self, monkeypatch):
        monkeypatch.setattr(locale, "getlocale", lambda: ("da_DK", "UTF-8"))
        with pytest.raises(RuntimeError, match="Your locale is set to"):
            _format_release_notes_date(datetime.date.fromisoformat("2021-01-01"))
