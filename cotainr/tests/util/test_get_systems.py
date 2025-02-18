"""
cotainr - a user space Apptainer/Singularity container builder.

Copyright DeiC, deic.dk
Licensed under the European Union Public License (EUPL) 1.2
- see the LICENSE file for details.

"""

import pytest

import cotainr.util

from .patches import (
    patch_empty_system,
    patch_system_with_actual_file,
    patch_system_with_badly_formatted_file,
    patch_system_with_non_existing_file,
)


class TestGetSystems:
    def test_non_existing(self, patch_system_with_non_existing_file):
        systems = cotainr.util.get_systems()

        assert isinstance(systems, dict)
        assert not systems

    def test_non_empty(self, patch_empty_system):
        systems = cotainr.util.get_systems()

        assert isinstance(systems, dict)
        assert not systems

    def test_actual_file(self, patch_system_with_actual_file):
        systems = cotainr.util.get_systems()

        assert isinstance(systems, dict)
        assert len(systems) == 2
        assert list(systems.keys())[0].startswith("some")
        assert list(systems.keys())[1].startswith("another")

    def test_badly_formatted_file(self, patch_system_with_badly_formatted_file):
        with pytest.raises(
            NameError,
            match="Error in systems.json: some_system_6021 missing argument base-image",
        ):
            cotainr.util.get_systems()
