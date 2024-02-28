from pathlib import Path

import pytest

from mkdocs_plantuml_local.PlantUMLLocal import PlantUMLLocal
from mkdocs_plantuml_local.config import PlantUMLLocalConfig


@pytest.fixture(scope="function", autouse=True)
def setup_fixtures(fs):
    fs.add_real_directory(Path(__file__).parent.joinpath("fixtures"))
    yield fs


@pytest.fixture(scope="function")
def plugin_factory():
    def make_plugin_class(shortname='plantuml',
                          background_colour='transparent',
                          class_name=None,
                          cache=False):
        config = PlantUMLLocalConfig()
        config.shortname = shortname
        config.background_colour = background_colour
        config.cache = cache
        if class_name:
            config.class_name = class_name

        plugin = PlantUMLLocal()
        plugin.config = config
        return plugin

    yield make_plugin_class
