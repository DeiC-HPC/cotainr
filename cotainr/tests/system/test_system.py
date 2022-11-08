from typing import Dict
from cotainr.system import SystemData
from .patches import (
    patch_empty_system,
    patch_system_with_actual_file,
    patch_system_with_non_existing_file,
)


class TestSystemData:
    def test_non_existing(self, patch_system_with_non_existing_file):
        systems = SystemData().get_systems()

        assert isinstance(systems, Dict)
        assert len(systems) == 0

    def test_non_empty(self, patch_empty_system):
        systems = SystemData().get_systems()

        assert isinstance(systems, Dict)
        assert len(systems) == 0

    def test_actual_file(self, patch_system_with_actual_file):
        systems = SystemData().get_systems()

        assert isinstance(systems, Dict)
        assert len(systems) == 2
        assert list(systems.keys())[0].startswith("some")
        assert list(systems.keys())[1].startswith("another")
