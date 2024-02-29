import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "mkdocs_version",
    [
        "1.5.3",
        "1.5.2",
        "1.5.1",
        "1.5.0",
        "1.4.3",
    ],
)
def test_with_mkdocs_version(mkdocs_version):
    with tempfile.TemporaryDirectory() as temp:
        install_plugin = subprocess.run(
            f"pip install .",
            cwd=Path(__file__).parent.parent.parent,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert install_plugin.returncode == 0

        install_mkdocs = subprocess.run(
            f"pip install mkdocs=={mkdocs_version}",
            cwd=temp,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert install_mkdocs.returncode == 0

        shutil.copytree(
            Path(__file__).parent.joinpath("fixtures", "input"),
            temp,
            dirs_exist_ok=True,
        )

        run_mkdocs_build = subprocess.run(
            f"mkdocs build",
            cwd=temp,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert run_mkdocs_build.returncode == 0

        assert (
            "mkdocs_plantuml_local: Rendering diagram 1 of page index.md"
            in run_mkdocs_build.stderr.decode("utf-8")
        )
        assert (
            "mkdocs_plantuml_local: Handled diagram 1 of page index.md in"
            in run_mkdocs_build.stderr.decode("utf-8")
        )
        assert "Documentation built" in run_mkdocs_build.stderr.decode("utf-8")

        created_cache_files = [
            str(f).replace(temp, "")
            for f in Path(temp).joinpath(".cache").glob("**/*")
            if f.is_file()
        ]

        assert (
            created_cache_files[0] == "/.cache/plantuml_local"
            "/c50fzkyTHubJdpR5b14l0iPPBTr4D14x1VvJ4ZvaP1Q"
            "/pIdGyucMROfhBbWUqtM43dEFyTwctEWkC6aqt4W6aeU"
            "/eHgNvJ3T-j3rtNN_mHPX0Ssqxc8c0iouXWbWVb9anDk"
        )
