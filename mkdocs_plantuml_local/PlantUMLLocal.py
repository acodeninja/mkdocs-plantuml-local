import json
import mkdocs.config.config_options
import mkdocs.config.defaults
import mkdocs.exceptions
import mkdocs.plugins
import mkdocs.structure.files
import mkdocs.structure.pages
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import time

from base64 import urlsafe_b64encode
from hashlib import sha256
from lxml import etree
from pathlib import Path


class PlantUMLLocalConfig(mkdocs.config.base.Config):
    shortname = mkdocs.config.config_options.Type(str, default='plantuml')
    background_colour = mkdocs.config.config_options.Type(str, default='transparent')
    class_name = mkdocs.config.config_options.Optional(
        mkdocs.config.config_options.Type(str, default=None),
    )
    cache = mkdocs.config.config_options.Type(bool, default=False)


class PlantUMLLocal(mkdocs.plugins.BasePlugin[PlantUMLLocalConfig]):
    def __init__(self):
        self._dependencies_checked = False
        self.plantuml_block = None
        self.logger = mkdocs.plugins.get_plugin_logger(__name__)

    def on_config(
            self,
            config: mkdocs.config.defaults.MkDocsConfig
    ) -> mkdocs.config.defaults.MkDocsConfig | None:
        self.plantuml_block = re.compile(rf'<pre class="{self.config.shortname}"')

    def on_post_page(self,
                     output: str,
                     *,
                     page: mkdocs.structure.pages.Page,
                     config: mkdocs.config.defaults.MkDocsConfig) -> str | None:
        if self.plantuml_block.findall(output):
            self._check_dependencies()
            html = etree.HTML(output)

            plantuml_blocks = html.cssselect('pre.plantuml')

            for index, block in enumerate(plantuml_blocks):
                start_time = time.time() * 1000
                plantuml_code = block.cssselect('code')[0]
                plantuml = ''.join(plantuml_code.itertext())

                svg = self._get_cached_diagram(page, plantuml)
                if svg is not None:
                    self.logger.info('Using cache for diagram '
                                     f'{index} of page {page.file.src_path}')
                else:
                    self.logger.info('Rendering diagram '
                                     f'{index} of page {page.file.src_path}')
                    svg = self._render_svg(plantuml)

                self._put_cached_diagram(page, plantuml, svg)

                block.getparent().replace(block, svg)
                end_time = time.time() * 1000
                self.logger.info(f'Handled diagram {index + 1} '
                                 f'of page {page.file.src_path} '
                                 f'in {end_time - start_time}ms')

            return etree.tostring(html, encoding=str, method="html")

        return output

    def _render_svg(self, plantuml):
        with tempfile.TemporaryDirectory() as temp:
            plantuml = self._inject_configuration(plantuml)
            plantuml_path = os.path.join(temp, 'diagram.puml')
            self._write_file(plantuml_path, plantuml)

            proc = subprocess.run(shlex.split(f"{shutil.which('java')} "
                                              f"-Djava.awt.headless=true "
                                              f"-jar {os.path.dirname(__file__)}/plantuml.jar "
                                              f"{plantuml_path} "
                                              "-tsvg"))

            if proc.returncode != 0:
                self.logger.error(proc.stderr)
                raise mkdocs.exceptions.PluginError('PlantUML failed to build the diagram, check '
                                                    'the logs above for more information.')

            svg_path = os.path.join(temp, next(
                file for file in os.listdir(temp) if file.endswith('.svg')))
            svg = self._read_file(svg_path)
            svg = svg.replace('<?xml version="1.0" encoding="us-ascii" standalone="no"?>', '')
            svg = etree.XML(svg)
            svg.attrib['preserveAspectRatio'] = "xMidYMid"
            svg.attrib['style'] = "width: auto; height: auto;"

            if self.config.class_name:
                svg.attrib['class'] = self.config.class_name

            return svg

    def _inject_configuration(self, plantuml):
        plantuml = plantuml.split("\n")
        try:
            plantuml.insert(plantuml.index('@enduml'),
                            f'skinparam backgroundcolor {self.config.background_colour}')
        except ValueError:
            self.logger.warning('Diagram does not contain UML, skipping set '
                                f'{self.config.background_colour} background')

        return "\n".join(plantuml)

    def _check_dependencies(self):
        if not self._dependencies_checked:
            if None in [shutil.which('java'), shutil.which('dot')]:
                raise mkdocs.exceptions.PluginError('Both java and dot must be available, try '
                                                    'installing openjdk and graphviz')
        self._dependencies_checked = True

    def _get_cached_diagram(self, page, plantuml):
        if not self.config.cache:
            return None

        diagram_path = self._generate_hash_path(page, plantuml)

        if diagram_path.exists():
            return etree.fromstring(diagram_path.read_bytes())

    def _generate_hash_path(self, page, plantuml):
        page_hash = self._string_hash(page.file.src_path)
        diagram_hash = self._string_hash(plantuml)
        config_hash = self._string_hash(json.dumps(list(self.config.values())))

        return Path(os.getcwd()).joinpath('.cache',
                                          'plantuml',
                                          config_hash,
                                          page_hash,
                                          diagram_hash)

    def _put_cached_diagram(self, page, plantuml, svg):
        if self.config.cache:
            path = self._generate_hash_path(page, plantuml)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(etree.tostring(svg))

    def _string_hash(self, plantuml):
        return urlsafe_b64encode(sha256(plantuml.encode('utf-8')).digest()).decode('utf-8').rstrip('=')

    @staticmethod
    def _write_file(path, content):
        fh = open(path, 'w')
        fh.write(content)
        fh.close()

    @staticmethod
    def _read_file(path):
        fh = open(path, 'r')
        contents = fh.read()
        fh.close()
        return contents
