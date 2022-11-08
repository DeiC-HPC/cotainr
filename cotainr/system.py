import json
from pathlib import Path


class SystemData:
    systems_file = (Path(__file__) / "../../systems.json").resolve()

    def get_systems(self):
        if self.systems_file.is_file():
            return json.load(open(self.systems_file))
        else:
            return {}
