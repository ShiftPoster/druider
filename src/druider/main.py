import logging
from pathlib import Path

from druider.app import DruidHelper
from druider.data import load_data


def main():
    root = logging.getLogger()
    root.setLevel(1)
    DruidHelper(load_data(Path.cwd() / "data.csv")).run()
