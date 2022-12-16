import argparse
from pathlib import Path
import shlex

import pytest

from cotainr.cli import Build, CotainrCLI
from ..container.patches import (
    patch_save_singularity_sandbox_context,
    patch_disable_singularity_sandbox_subprocess_runner,
)
from ..pack.patches import (
    patch_disable_conda_install_bootstrap_conda,
    patch_disable_conda_install_download_conda_installer,
)
from ..util.patches import patch_system_with_actual_file, patch_empty_system


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
    def test_already_existing_file_but_no(self, answer, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: answer)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Path(image_path).touch()
        with pytest.raises(SystemExit):
            Build(image_path=image_path, base_image=base_image)

    @pytest.mark.parametrize("answer", ["y", "Y"])
    def test_already_existing_file(self, answer, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: answer)
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Path(image_path).touch()
        build = Build(image_path=image_path, base_image=base_image)
        assert build.base_image == base_image


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

    def test_specifying_both_system_and_base_image(self, capsys):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        system = "some_system_6021"
        parser = argparse.ArgumentParser()
        Build.add_arguments(parser=parser)

        with pytest.raises(SystemExit):
            args = parser.parse_args(
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


class TestExecute:
    def test_default_container_build(
        self, patch_disable_singularity_sandbox_subprocess_runner, capsys
    ):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        Build(image_path=image_path, base_image=base_image).execute()
        sandbox_create_cmd, sandbox_build_cmd = (
            capsys.readouterr().out.strip().split("\n")
        )
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
        patch_disable_conda_install_download_conda_installer,
        patch_save_singularity_sandbox_context,
        capsys,
    ):
        image_path = "some_image_path_6021"
        base_image = "some_base_image_6021"
        conda_env = "some_conda_env_6021"
        conda_env_content = "Some conda env content 6021"
        Path(conda_env).write_text(conda_env_content)
        Build(
            image_path=image_path, base_image=base_image, conda_env=conda_env
        ).execute()

        # Check that conda_env file has been copied to container
        assert Path(f"./saved_sandbox_dir/{conda_env}").read_text() == conda_env_content

        # Check that the singularity environment has been updated activate conda env
        assert (
            Path("./saved_sandbox_dir/environment")
            .read_text()
            .strip()
            .endswith("conda activate conda_container_env")
        )

        # Check sandbox interaction commands
        (
            sandbox_create_cmd,
            conda_bootstrap_cmd,
            conda_bootstrap_clean_cmd,
            conda_env_create_cmd,
            conda_clean_cmd,
            sandbox_build_cmd,
        ) = (
            capsys.readouterr().out.strip().split("\n")
        )
        assert sandbox_create_cmd.startswith("PATCH: Ran command in sandbox:")
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


class TestHelpMessage:
    def test_CLI_subcommand_help_message(self, argparse_options_line, capsys):
        with pytest.raises(SystemExit):
            CotainrCLI(args=["build", "--help"])
        stdout = capsys.readouterr().out
        assert stdout == (
            # Capsys apparently assumes an 80 char terminal (?) - thus extra '\n'
            "usage: cotainr build [-h] (--base-image BASE_IMAGE | --system SYSTEM)\n"
            "                     [--conda-env CONDA_ENV]\n"
            "                     image_path\n\n"
            "Build a container.\n\n"
            "positional arguments:\n"
            "  image_path            path to the built container image\n\n"
            f"{argparse_options_line}"
            "  -h, --help            show this help message and exit\n"
            "  --base-image BASE_IMAGE\n"
            "                        base image to use for the container which may be any\n"
            "                        valid apptainer/singularity <build spec>\n"
            "  --system SYSTEM       which system/partition you will be running the\n"
            "                        container on, will set base image and other parameters\n"
            "                        for a simpler container creation. running the info\n"
            "                        command will tell you more about the system and what\n"
            "                        is available\n"
            "  --conda-env CONDA_ENV\n"
            "                        path to a conda environment.yml file to install and\n"
            "                        activate in the container\n"
        )
