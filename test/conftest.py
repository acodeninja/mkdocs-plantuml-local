import tempfile
from pathlib import Path
from unittest import mock
from unittest.mock import patch

import pytest

from mkdocs_plantuml_local.PlantUMLLocal import PlantUMLLocal
from mkdocs_plantuml_local.config import PlantUMLLocalConfig


@pytest.fixture(scope="function", autouse=True)
def setup_fixtures(fs):
    temp = tempfile.TemporaryDirectory()
    temp.name = '/temporary/test'
    Path(temp.name).mkdir(parents=True, exist_ok=True)
    with mock.patch.object(tempfile, "TemporaryDirectory", return_value=temp):
        fixtures_path = Path(__file__).parent.joinpath("fixtures")
        fs.add_real_directory(fixtures_path)
        fs.add_real_file(fixtures_path.joinpath("rendered_sample.svg"),
                         False,
                         Path(temp.name).joinpath("diagram.svg"))
        yield fixtures_path


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
