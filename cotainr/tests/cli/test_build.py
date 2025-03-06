"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import argparse
from pathlib import Path
import re
import shlex

import pytest

from cotainr.cli import Build, CotainrCLI

from ..container.patches import (
    patch_disable_add_metadata,
    patch_disable_singularity_sandbox_subprocess_runner,
    patch_fake_singularity_sandbox_env_folder,
    patch_save_singularity_sandbox_context,
)
from ..pack.patches import (
    patch_disable_conda_install_bootstrap_conda,
    patch_disable_conda_install_display_miniforge_license_for_acceptance,
    patch_disable_conda_install_download_miniforge_installer,
)
from ..tracing.patches import patch_disable_console_spinner
from ..util.patches import patch_empty_system, patch_system_with_actual_file


class TestConstructor:
    def test_nonexisting_conda_env(self):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        with pytest.raises(FileNotFoundError) as exc_info:
            Build(image_path=image_path, base_image=base_image, conda_env=conda_env)
        exc_msg = str(exc_info.value)
        assert exc_msg.startswith("The provided Conda env file '")
        assert exc_msg.endswith("' does not exist.")
        assert conda_env in exc_msg

    @pytest.mark.parametrize(
        "base_image,system",
        [("some_base_image_6021", None), (None, "some_system_6021")],
    )
    def test_only_specifying_required_args(
        self, base_image, system, patch_system_with_actual_file
    ):
        # See also the matching TestAddArguments test below
        image_path = "some_image_path_6021"
        build = Build(image_path=image_path, base_image=base_image, system=system)
        assert build.image_path.is_absolute()
        assert build.image_path.name == image_path
        if system is not None:
            base_image = "some_base_image_6021"
            assert build.system["base-image"] == base_image
            assert build.base_image == base_image
        else:
            assert build.base_image == base_image
        assert build.conda_env is None
        assert not build.accept_licenses
        assert build.log_settings.verbosity == 0
        assert build.log_settings.log_file_path is None
        assert not build.log_settings.no_color

    @pytest.mark.parametrize(
        "base_image,system",
        [("some_base_image_6021", None), (None, "some_system_6021")],
    )
    def test_specifying_conda_env(
        self, base_image, system, patch_system_with_actual_file
    ):
        # See also the matching TestAddArguments test below
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        Path(conda_env).touch()
        build = Build(
            image_path=image_path,
            base_image=base_image,
            system=system,
            conda_env=conda_env,
        )
        assert build.conda_env.is_absolute()
        assert build.conda_env.name == conda_env

    def test_specifying_non_existing_system(self, patch_empty_system):
        image_path = "some_image_path_6021"
        system = "some_system_6021"
        with pytest.raises(KeyError, match="System does not exist"):
            Build(image_path=image_path, system=system)

    @pytest.mark.parametrize("answer", ["n", "N", "", "some_answer_6021"])
    def test_already_existing_file_but_no(
        self, answer, factory_mock_input, monkeypatch
    ):
        monkeypatch.setattr("builtins.input", factory_mock_input(answer))
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Path(image_path).touch()
        with pytest.raises(SystemExit):
            Build(image_path=image_path, base_image=base_image)

    @pytest.mark.parametrize("answer", ["y", "Y"])
    def test_already_existing_file(self, answer, factory_mock_input, monkeypatch):
        monkeypatch.setattr("builtins.input", factory_mock_input(answer))
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Path(image_path).touch()
        build = Build(image_path=image_path, base_image=base_image)
        assert build.base_image == base_image

    def test_specifying_accept_licenses(self):
        # See also the matching TestAddArguments test below
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        build = Build(
            image_path=image_path, base_image=base_image, accept_licenses=True
        )
        assert build.accept_licenses

    def test_specifying_log_to_file(self):
        # See also the matching TestAddArguments test below
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        build = Build(image_path=image_path, base_image=base_image, log_to_file=True)
        print(
            build.log_settings.log_file_path.name,
        )
        assert re.match(
            r"^cotainr_build_\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2}\.\d{6}$",
            build.log_settings.log_file_path.name,
        )

    def test_specifying_no_color(self):
        # See also the matching TestAddArguments test below
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        build = Build(image_path=image_path, base_image=base_image, no_color=True)
        assert build.log_settings.no_color


class TestAddArguments:
    def test_not_specifying_base_image_or_system(self, capsys):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser(prog="some_prog_name_6021")
        Build.add_arguments(parser=parser)
        with pytest.raises(SystemExit):
            parser.parse_args(args=shlex.split("some_image_path_6021"))
        stderr = capsys.readouterr().err
        assert stderr.strip().endswith(
            "some_prog_name_6021: error: one of the arguments --base-image --system is required"
        )

    def test_only_specifying_required_args_base_image(self):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(f"{image_path} --base-image={base_image}")
        )
        assert isinstance(args.image_path, Path)
        assert args.image_path.name == image_path
        assert isinstance(args.base_image, str)
        assert args.base_image == base_image
        assert not args.accept_licenses

    def test_only_specifying_required_args_system(self, patch_system_with_actual_file):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        system = "some_system_6021"
        args = parser.parse_args(args=shlex.split(f"{image_path} --system={system}"))
        assert isinstance(args.image_path, Path)
        assert args.image_path.name == image_path
        assert isinstance(args.system, str)
        assert args.system == system
        assert not args.accept_licenses

    def test_specifying_both_system_and_base_image(self, capsys):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        system = "some_system_6021"
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)

        with pytest.raises(SystemExit):
            parser.parse_args(
                args=shlex.split(
                    f"{image_path} --system {system} --base-image {base_image}"
                )
            )
        stderr = capsys.readouterr().err
        assert stderr.strip().endswith(
            "argument --base-image: not allowed with argument --system"
        )

    def test_specifying_conda_env_arg(self):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        args = parser.parse_args(
            args=shlex.split(
                f"{image_path} --base-image={base_image} --conda-env={conda_env}"
            )
        )
        assert isinstance(args.conda_env, Path)
        assert args.conda_env.name == conda_env

    def test_specifying_accept_licenses(self):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(
                f"{image_path} --base-image={base_image} --accept-licenses"
            )
        )
        assert args.accept_licenses

    @pytest.mark.parametrize(
        ["verbose_arg", "verbosity"],
        [
            ("--verbose", 1),
            ("--verbose --verbose", 2),
            ("-v", 1),
            ("-vv", 2),
            ("-vvv", 3),
            ("-vvvv", 4),
        ],
    )
    def test_specifying_verbose(self, verbose_arg, verbosity):
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(f"{image_path} --base-image={base_image} {verbose_arg}")
        )
        assert args.verbosity == verbosity

    @pytest.mark.parametrize(
        ["verbose_arg", "verbosity"],
        [
            ("--quiet", -1),
            ("--quiet --quiet", -1),
            ("-q", -1),
            ("-qq", -1),
        ],
    )
    def test_specifying_quiet(self, verbose_arg, verbosity):
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(f"{image_path} --base-image={base_image} {verbose_arg}")
        )
        assert args.verbosity == verbosity

    def test_specifying_both_verbose_and_quiet(self, capsys):
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"

        with pytest.raises(SystemExit):
            parser.parse_args(
                args=shlex.split(
                    f"{image_path} --base-image={base_image} --verbose --quiet"
                )
            )
        stderr = capsys.readouterr().err
        assert stderr.strip().endswith(
            "argument --quiet/-q: not allowed with argument --verbose/-v"
        )

    def test_specifying_log_to_file(self):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(f"{image_path} --base-image={base_image} --log-to-file")
        )
        assert args.log_to_file

    def test_specifying_no_color(self):
        # See also the matching TestConstructor test above
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        args = parser.parse_args(
            args=shlex.split(f"{image_path} --base-image={base_image} --no-color")
        )
        assert args.no_color


class TestExecute:
    def test_default_container_build(
        self,
        patch_disable_singularity_sandbox_subprocess_runner,
        # add_metadata fails as there is no sandbox_dir and labels.json since
        # we request patch_disable_singularity_sandbox_subprocess_runner.
        patch_disable_add_metadata,
        patch_disable_console_spinner,
        capsys,
    ):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Build(image_path=image_path, base_image=base_image).execute()
        (sandbox_create_cmd, sandbox_uname_cmd, sandbox_build_cmd) = (
            capsys.readouterr().out.strip().split("\n")
        )

        assert "'uname', '-m'" in sandbox_uname_cmd
        assert sandbox_create_cmd.startswith("PATCH: Ran command in sandbox:")
        assert all(
            s in sandbox_create_cmd
            for s in ["'singularity'", "'build'", "'--sandbox'", f"'{base_image}'"]
        )
        assert sandbox_build_cmd.startswith("PATCH: Ran command in sandbox:")
        assert all(
            s in sandbox_build_cmd
            for s in ["'singularity'", "'build'", f"{image_path}"]
        )

    def test_include_conda_env(
        self,
        patch_disable_singularity_sandbox_subprocess_runner,
        patch_disable_conda_install_bootstrap_conda,
        patch_disable_conda_install_download_miniforge_installer,
        patch_fake_singularity_sandbox_env_folder,
        patch_save_singularity_sandbox_context,
        patch_disable_add_metadata,
        patch_disable_console_spinner,
        caplog,
        capsys,
    ):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        conda_env_content = "Some conda env content 6021"
        saved_sandbox_dir = Path(f"./{patch_save_singularity_sandbox_context}")
        Path(conda_env).write_text(conda_env_content)
        Build(
            image_path=image_path,
            base_image=base_image,
            conda_env=conda_env,
            accept_licenses=True,
        ).execute()

        # Check that conda_env file has been copied to container
        assert (saved_sandbox_dir / f"{conda_env}").read_text() == conda_env_content

        # Check that the singularity environment has been updated activate conda env
        assert (
            (saved_sandbox_dir / ".singularity.d/env/92-cotainr-env.sh")
            .read_text()
            .strip()
            .endswith("conda activate conda_container_env")
        )

        # Check sandbox interaction commands
        (
            sandbox_create_cmd,
            sandbox_uname_cmd,
            conda_bootstrap_cmd,
            conda_bootstrap_clean_cmd,
            conda_env_create_cmd,
            conda_clean_cmd,
            sandbox_build_cmd,
        ) = capsys.readouterr().out.strip().split("\n")
        assert sandbox_create_cmd.startswith("PATCH: Ran command in sandbox:")
        assert "'uname', '-m'" in sandbox_uname_cmd
        assert all(
            s in sandbox_create_cmd
            for s in ["'singularity'", "'build'", "'--sandbox'", f"'{base_image}'"]
        )
        assert conda_bootstrap_cmd.startswith("PATCH: Bootstrapped Conda using")
        assert conda_bootstrap_clean_cmd.startswith("PATCH: Ran command in sandbox:")
        assert "'conda', 'clean'" in conda_bootstrap_clean_cmd
        assert conda_env_create_cmd.startswith("PATCH: Ran command in sandbox:")
        assert all(
            s in conda_env_create_cmd
            for s in [
                "'conda'",
                "'env'",
                "'create'",
                f"{conda_env}",
                "'conda_container_env'",
            ]
        )
        assert conda_clean_cmd.startswith("PATCH: Ran command in sandbox:")
        assert "'conda', 'clean'" in conda_clean_cmd
        assert sandbox_build_cmd.startswith("PATCH: Ran command in sandbox:")
        assert all(
            s in sandbox_build_cmd
            for s in ["'singularity'", "'build'", f"{image_path}"]
        )

        # Check log calls
        assert re.search(
            r"^WARNING  CondaInstall\.err\:pack\.py\:(\d+) "
            r"You have accepted the Miniforge installer license via the command line option "
            r"'--accept-licenses'\.$",
            caplog.text,
            flags=re.MULTILINE,
        )

    def test_no_beforehand_license_acceptance(
        self,
        patch_disable_singularity_sandbox_subprocess_runner,
        patch_disable_conda_install_download_miniforge_installer,
        patch_disable_conda_install_display_miniforge_license_for_acceptance,
    ):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        conda_env_content = "Some conda env content 6021"
        Path(conda_env).write_text(conda_env_content)
        with pytest.raises(SystemExit, match="^PATCH: Showing license terms for "):
            Build(
                image_path=image_path,
                base_image=base_image,
                conda_env=conda_env,
                accept_licenses=False,
            ).execute()


class TestHelpMessage:
    def test_CLI_subcommand_help_message(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=["build", "--help"])
        stdout = capsys.readouterr().out
        assert stdout == (
            # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
            "usage: cotainr build [-h] (--base-image BASE_IMAGE | --system SYSTEM)\n"
            "                     [--conda-env CONDA_ENV] [--accept-licenses]\n"
            "                     [--verbose | --quiet] [--log-to-file] [--no-color]\n"
            "                     image_path\n\n"
            "Build a container.\n\n"
            "positional arguments:\n"
            "  image_path            path to the built container image\n\n"
            f"{argparse_options_line}"
            "  -h, --help            show this help message and exit\n"
            "  --base-image BASE_IMAGE\n"
            "                        base image to use for the container which may be any\n"
            "                        valid Apptainer/Singularity <BUILD SPEC>\n"
            "  --system SYSTEM       which system/partition you will be running the\n"
            "                        container on. This sets base image and other\n"
            "                        parameters for a simpler container creation. Running\n"
            "                        the info command will tell you more about the system\n"
            "                        and what is available\n"
            "  --conda-env CONDA_ENV\n"
            "                        path to a Conda environment.yml file to install and\n"
            "                        activate in the container. When installing a Conda\n"
            "                        environment, you must accept the Miniforge license\n"
            "                        terms, as specified during the build process\n"
            "  --accept-licenses     accept all license terms (if any) needed for\n"
            "                        completing the container build process\n"
            "  --verbose, -v         increase the verbosity of the output from cotainr. Can\n"
            "                        be used multiple times: Once for subprocess output,\n"
            "                        twice for subprocess INFO, three times for DEBUG, and\n"
            "                        four times for TRACE\n"
            "  --quiet, -q           do not show any non-CRITICAL output from cotainr\n"
            "  --log-to-file         create files containing all logging information shown\n"
            "                        on stdout/stderr\n"
            "  --no-color            do not use colored console output\n"
        )
