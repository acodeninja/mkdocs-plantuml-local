from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

import mkdocs.exceptions
import pytest

from mkdocs_plantuml_local.render import render


@patch("mkdocs_plantuml_local.render.subprocess.run")
@patch("mkdocs_plantuml_local.render.shutil.which")
def test_render_plantuml(shutil_which, subprocess_run, setup_fixtures):
    shutil_which.return_value = "java"
    subprocess_run.return_value = MagicMock(returncode=0)

    render(setup_fixtures.joinpath("sample.puml").read_text())

    subprocess_run.assert_called_once_with(
        ["java", "-Djava.awt.headless=true", "-jar", ANY, ANY, "-tsvg"]
    )


@patch("mkdocs_plantuml_local.render.subprocess.run")
@patch("mkdocs_plantuml_local.render.shutil.which")
def test_render_plantuml_when_subprocess_fails(
    shutil_which, subprocess_run, setup_fixtures
):
    shutil_which.return_value = "java"
    subprocess_run.return_value = MagicMock(returncode=1)

    with pytest.raises(mkdocs.exceptions.PluginError) as e:
        render(setup_fixtures.joinpath("sample.puml").read_text())

    assert e.value.message == (
        "PlantUML failed to build the diagram, "
        "check the logs above for more information."
    )

    subprocess_run.assert_called_once_with(
        ["java", "-Djava.awt.headless=true", "-jar", ANY, ANY, "-tsvg"]
    )
