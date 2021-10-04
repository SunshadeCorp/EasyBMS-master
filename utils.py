from pathlib import Path
from typing import Dict

import yaml


def get_config(filename: str) -> Dict:
    with open(Path(__file__).parent / filename, 'r') as file:
        try:
            cfg = yaml.safe_load(file)
            return cfg
        except yaml.YAMLError as e:
            print(e)
