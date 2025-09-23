"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import builtins
import contextlib
from contextlib import contextmanager
import io
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys
from time import sleep
import urllib.error
import urllib.request

import pytest


@pytest.fixture
def argparse_options_line():
    """
    Return the help text line for optional arguments in argparse.

    Apparently this line changed from "optional arguments" to "options" in Python 3.10.
    """
    py_ver = sys.version_info
    if py_ver.major > 3 or (py_ver.major == 3 and py_ver.minor >= 10):
        return "options:\n"
    else:
        return "optional arguments:\n"


@pytest.fixture
def context_importerror(monkeypatch):
    """
    Force an ImportError when importing the a specified module.

    The `mock_import_context` contextmanager forces an `ImportError` to be
    raised when trying to import the `module_name` module within the context.
    Imports of all other modules are unaffected.
    """

    @contextlib.contextmanager
    def mock_import_context(module_name):
        builtins_import = builtins.__import__

        def mock_import(name, globals, locals, fromlist, level):
            if name == module_name:
                raise ImportError(f"PATCH: ImportError forced for {module_name=}")
            else:
                return builtins_import(name, globals, locals, fromlist, level)

        with monkeypatch.context() as m:
            m.setattr("builtins.__import__", mock_import)
            yield

    return mock_import_context


@pytest.fixture(autouse=True)
def context_reload_logging():
    """
    Reset the internal state of the logging module on test teardown.

    Needed in tests of logging functionality where the tests end up affecting
    the internal state of the logging module.

    The current implementation is based on:
    https://til.tafkas.net/posts/-resetting-python-logging-before-running-tests/

    It used to be implemented as `importlib.reload(logging)`. However, it turns
    out that this simpler approach does not work for some tests where multiple
    test cases use the caplog fixture. For those cases, only the first test
    case would actually capture the log messages - the others would be empty.
    See this GH PR comment for an in-depth discussion of the issue:
    https://github.com/DeiC-HPC/cotainr/pull/154#discussion_r2166428044
    """
    yield
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    loggers.append(logging.getLogger())
    for logger in loggers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(logging.NOTSET)
        logger.propagate = True
        logger.manager.loggerDict = {}


@pytest.fixture
def context_set_umask():
    """Return a context manager providing a context with the specified umask."""

    @contextlib.contextmanager
    def set_umask(umask):
        current_umask = None
        try:
            current_umask = os.umask(umask)
            yield
        finally:
            if current_umask is not None:
                os.umask(current_umask)

    return set_umask


@pytest.fixture
def data_log_level_names_mapping():
    """
    A mapping from log levels to their names.

    From Python 3.11 this mapping is also available as
    logging.getLevelNamesMapping().
    """
    level_names_mapping = {
        level: logging.getLevelName(level)
        for level in [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ]
    }

    return level_names_mapping


@pytest.fixture
def factory_mock_input():
    """
    Create mock of the builtins `input` function that returns a fixed "input".

    Returns a factory for creating mocked versions of the builtin `input`
    function to be used with the `monkeypatch` fixture to replace
    `builtins.input` with a function that prints the prompt (its argument, if
    provided) and returns a "fixed user input", provided as argument to the
    factory.
    """

    def create_mock_input(fixed_user_input=None):
        def mock_input(prompt):
            print(prompt, end="")
            return fixed_user_input

        return mock_input

    return create_mock_input


@pytest.fixture
def factory_mock_input_sequence():
    """
    Create mock of the builtins `input` function that returns a sequence of "inputs".

    Returns a factory for creating mocked versions of the builtin `input`
    function to be used with the `monkeypatch` fixture to replace
    `builtins.input` with a function that prints the prompt (its argument, if
    provided) and returns the "next user input" from a sequence, provided as
    argument to the factory.

    If more inputs are requested than provided in the sequence, a
    `StopIteration` exception is raised.
    """

    def create_mock_input(user_input_sequence=(None,)):
        inputs = iter(user_input_sequence)

        def mock_input(prompt):
            print(prompt, end="")
            return next(inputs)

        return mock_input

    return create_mock_input


@pytest.fixture
def patch_urllib_urlopen_as_bytes_stream(monkeypatch):
    """
    Disable urllib.request.urlopen(...).

    The `urlopen` contextmanager is replaced by a mock that returns a bytes
    message about the URL content that would have been opened.
    """

    @contextlib.contextmanager
    def mock_urlopen(url, *args, **kwargs):
        yield io.BytesIO(f"PATCH: Bytes returned by urlopen for {url=}".encode())

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)


@pytest.fixture
def patch_urllib_urlopen_force_fail(monkeypatch):
    """
    Force urllib.request.urlopen(...) to raise URLError.

    The `urlopen` contextmanager is replaced by a mock that always raises an
    `urllib.error.URLError` when entering the contextmanager.
    """

    @contextlib.contextmanager
    def mock_urlopen(url, *args, **kwargs):
        raise urllib.error.URLError(f"PATCH: urlopen error forced for {url=}")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)


@pytest.fixture(autouse=True)
def safedir(tmp_path):
    """
    Force test to be run in a temporary directory.

    A lot of the functionality in cotainr manipulates directories. In order to
    provide some protection against messing up the current working directory by
    running a test, we force all tests to run from a temporary directory by
    making this an "autouse" fixture.
    """
    origin = Path().resolve()
    safe_dir = tmp_path / "safe_dir"
    safe_dir.mkdir()
    os.chdir(safe_dir)
    yield
    os.chdir(origin)


@pytest.fixture
def singularity_exec():
    """
    Provide a function wrapping a "singularity exec" call.

    The function returned by this fixture provides a shorthand to run
    "singularity exec {cmd}" as a python subprocess.
    """

    def _singularity_exec(cmd):
        singularity_process = subprocess.run(
            ["singularity", "exec", *shlex.split(cmd)],
            capture_output=True,
            check=True,
            text=True,
        )

        return singularity_process

    return _singularity_exec


@pytest.fixture
def singularity_inspect():
    """Provide a function wrapping a "singularity inspect" call."""
    return lambda container_path: subprocess.run(
        ["singularity", "inspect", container_path],
        capture_output=True,
        check=True,
        text=True,
    )


@pytest.fixture(scope="session")
def files(request):
    """
    Reuse files using the PyTest cache.

    Clear cache using `pytest --cache-clear`.

    Usage::

        def test_conda(files):
            path = files['conda_installer']
            ...
    """
    cache = request.config.cache
    cache_dir = cache.mkdir("test_files")

    allfiles = fileFactory(cache_dir)
    yield allfiles


class fileFactory:
    def __init__(self, folder):
        self.folder = folder

        self.cached_files = {}
        for fil in folder.glob("**/*.*"):
            self.cached_files[fil.name] = fil

    def __getitem__(self, name):
        if name in self.cached_files:
            return self.cached_files[name]

        # Each cached object has its own filepath in .pytest_cache/d/test_files/
        filepath = self.folder / name
        for _ in range(60):
            if filepath.exists():
                # Functions can choose arbitrary name for file so we glob for it
                # XXX Consider using generated_file name instead, but how to get it before try...
                myFile = [i for i in filepath.glob("*.*")]
                assert len(myFile) == 1, (
                    "Multiple cache files per folder is not supported"
                )
                self.cached_files[name] = filepath / myFile[0]
                return self.cached_files[name]

            try:
                with lock(self.folder / f"{name}.lock"):
                    work_path = filepath.with_name(f"{filepath.name}-tmp")
                    work_path.mkdir(exist_ok=True)
                    generated_file = getattr(self, name)(work_path)

                    assert generated_file.is_file()
                    assert generated_file.exists()
                    work_path.rename(filepath)

            except Locked:
                sleep(1)

        raise RuntimeError(
            f"{self.__class__.__name__} fixture generation "
            f"takes too long: {name}.  Consider using pytest "
            "--cache-clear if there are stale lockfiles"
        )

    ### Recipes for creating cached files ###
    def conda_installer(self, work_path):
        from cotainr.comm import CommunicationInterface
        from cotainr.pack import Conda
        from cotainr.util import cpath

        comm = CommunicationInterface(exec_default=[])
        conda = Conda(comm=comm)
        my_work_cfile = cpath(container_directory="/", path=work_path)
        install_path = conda.download_miniforge(
            location_cfile=my_work_cfile, architecture="x86_64", license_accepted=True
        )
        return install_path.path

    def generic_sif(self, image_path, image):
        subprocess.run(
            args=["singularity", "pull", str(image_path.resolve()), image],
            capture_output=True,
            check=True,
            text=True,
        )
        return image_path

    def alpine_sif(self, work_path):
        return self.generic_sif(
            work_path / "alpine_latest.sif", "docker://alpine:latest"
        )

    def ubuntu_sif(self, work_path):
        return self.generic_sif(
            work_path / "ubuntu_latest.sif", "docker://ubuntu:latest"
        )

    def conda_sif(self, work_path):
        from cotainr.container import SingularitySandbox
        from cotainr.pack import Conda
        from cotainr.tracing import LogSettings

        log = LogSettings()
        install_path = self["conda_installer"]

        with SingularitySandbox(
            base_image=self["ubuntu_sif"], prefix=str(work_path) + "/", log_settings=log
        ) as sandbox:
            conda = Conda(comm=sandbox.comm, log_settings=log)
            local_install_path = sandbox.sandbox_dir / "conda_installer.sh"
            sandbox.comm.copy(
                install_path, local_install_path, log_dispatcher=conda.log_dispatcher
            )
            conda.install(local_install_path)
            sandbox.comm.add(
                filename=sandbox.env_file, log_dispatcher=sandbox.log_dispatcher
            )

            assert sandbox.env_file.host_path.exists()
            conda.source_install(env_file=sandbox.env_file)
            conda.verify_install()
            conda.update_conda()  # Requires conda connection
            sandbox.build_image(path=work_path / "conda.sif")

        return work_path / "conda.sif"


class Locked(FileExistsError):
    pass


@contextmanager
def lock(path):
    fd = None
    try:
        with path.open("x") as fd:
            yield
    except FileExistsError:
        raise Locked() from None
    finally:
        if fd is not None:
            path.unlink()
