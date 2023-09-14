from lxml import etree
import mkdocs.config.config_options
import mkdocs.config.defaults
import mkdocs.exceptions
import mkdocs.plugins
import mkdocs.structure.files
import mkdocs.structure.pages
import os
import re
import shutil
import subprocess
import tempfile
import time


class PlantUMLLocalConfig(mkdocs.config.base.Config):
    shortname = mkdocs.config.config_options.Type(str, default='plantuml')
    background_colour = mkdocs.config.config_options.Type(str, default='transparent')


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
                plantuml_code = block.cssselect('code')[0]
                plantuml = ''.join(plantuml_code.itertext())
                start_time = time.time() * 1000
                svg = self._render_svg(plantuml)
                end_time = time.time() * 1000
                self.logger.info(f'Rendered diagram {index+1} '
                                 f'of page {page.file.src_path} '
                                 f'in {end_time - start_time}ms')
                block.getparent().replace(block, svg)

            return etree.tostring(html, encoding=str, method="html")

        return output

    def _render_svg(self, plantuml):
        with tempfile.TemporaryDirectory() as temp:
            plantuml = plantuml.split("\n")
            plantuml.insert(plantuml.index('@enduml'),
                            f'skinparam backgroundcolor {self.config.background_colour}')
            plantuml = "\n".join(plantuml)
            puml_path = os.path.join(temp, 'diagram.puml')
            self._write_file(puml_path, plantuml)

            proc = subprocess.run(f"{shutil.which('java')} -jar "
                                  f"{os.path.dirname(__file__)}/plantuml.jar "
                                  f"{puml_path} "
                                  "-tsvg".split(' '))

            if proc.returncode != 0:
                self.logger.error(proc.stderr)
                raise mkdocs.exceptions.PluginError('PlantUML failed to build the diagram, check '
                                                    'the logs above for more information.')

            svg_path = os.path.join(temp, next(
                file for file in os.listdir(temp) if file.endswith('.svg')))
            svg = self._read_file(svg_path)
            svg = svg.replace('<?xml version="1.0" encoding="us-ascii" standalone="no"?>', '')
            return etree.XML(svg)

    def _check_dependencies(self):
        if not self._dependencies_checked:
            if None in [shutil.which('java'), shutil.which('dot')]:
                raise mkdocs.exceptions.PluginError('Both java and dot must be available, try '
                                                    'installing openjdk and graphviz')
        self._dependencies_checked = True

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
