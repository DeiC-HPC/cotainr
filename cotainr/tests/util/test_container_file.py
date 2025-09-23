"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

from pathlib import Path

import pytest

from cotainr.util import cpath


class TestCfile:
    @staticmethod
    def test_host_path():
        path1 = "/internal/container/path/"
        cfile1 = cpath(path1)

        with pytest.raises(AttributeError):
            _ = cfile1.container_directory

        with pytest.raises(AttributeError):
            _ = cfile1.host_path

        cfile2 = cpath(path1, container_directory="/")
        assert cfile2.container_directory == Path("/")
        assert cfile2.host_path == cfile2.path

    @staticmethod
    def test_from_hostpath():
        host_path = "/path/to/container/internal/container/path/"
        cfile = cpath.from_hostpath(
            host_path=host_path, container_directory="/path/to/container/"
        )
        assert cfile.host_path == Path(host_path)
        assert cfile.path == Path("/internal/container/path/")

    @staticmethod
    def test_cfile_append():
        cdir = "/path/to/container"
        path1 = "/internal/container/path/"
        cfile1 = cpath(path1, cdir)

        test1 = cfile1 / "file.txt"
        assert test1.path == Path("/internal/container/path/file.txt")

        abs_path = "/some/file.txt"
        test2 = cfile1 / abs_path
        assert test2.path == Path(abs_path)

        cfile2 = cpath("file.txt", cdir)
        test3 = cfile1 / cfile2
        assert test3.path == Path("/internal/container/path/file.txt")

        cfile3 = cpath("", cdir)
        test4 = cfile3 / "conda_installer.sh"
        test4_copy = cpath("conda_installer.sh", cdir)
        assert test4.path == test4_copy.path
        assert test4.host_path == test4_copy.host_path
