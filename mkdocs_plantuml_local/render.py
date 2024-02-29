import mkdocs.exceptions
import shlex
import shutil
import subprocess
import tempfile

from pathlib import Path


def render(plantuml):
    with tempfile.TemporaryDirectory() as temp:
        plantuml_path = Path(temp).joinpath('diagram.puml')
        plantuml_path.write_text(plantuml)

        proc = subprocess.run(shlex.split(f"{shutil.which('java')} "
                                          f"-Djava.awt.headless=true "
                                          f"-jar {Path(__file__).parent}/plantuml.jar "
                                          f"{plantuml_path} "
                                          "-tsvg"))

        output_path = Path(temp).joinpath('diagram.svg')

        if proc.returncode != 0 or not output_path.exists():
            raise mkdocs.exceptions.PluginError('PlantUML failed to build the diagram, check '
                                                'the logs above for more information.')

        svg = output_path.read_text()
        svg = svg.replace('<?xml version="1.0" encoding="us-ascii" standalone="no"?>',
                          '')

        return svg
