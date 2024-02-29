from unittest.mock import patch

import mkdocs.exceptions
import pytest

from mkdocs_plantuml_local.dependencies import check_dependencies


@pytest.mark.parametrize(
    "missing_dependencies",
    [
        ["java"],
        ["dot"],
        ["dot", "java"],
    ],
)
def test_check_dependencies(missing_dependencies):
    with patch("mkdocs_plantuml_local.dependencies.shutil.which") as which:

        def missing(d):
            return None if d in missing_dependencies else d

        which.side_effect = missing

        with pytest.raises(mkdocs.exceptions.PluginError) as error:
            check_dependencies()

        assert error.value.message == "Missing dependencies: {}".format(
            ", ".join(missing_dependencies)
        )
