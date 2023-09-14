import re
import subprocess
import tempfile
from os import listdir

import mkdocs.config.config_options
import mkdocs.plugins
import mkdocs.structure.pages
import mkdocs.structure.files
from mkdocs.config.defaults import MkDocsConfig
from os.path import join, dirname


class PlantUMLLocalConfig(mkdocs.config.base.Config):
    shortname = mkdocs.config.config_options.Type(str, default='plantuml')
    background_colour = mkdocs.config.config_options.Type(str, default='transparent')


class PlantUMLLocal(mkdocs.plugins.BasePlugin[PlantUMLLocalConfig]):
    def on_page_markdown(self,
                         markdown: str,
                         page: mkdocs.structure.pages.Page,
                         config: MkDocsConfig,
                         files: mkdocs.structure.files.Files):
        log = mkdocs.plugins.get_plugin_logger('plantuml-local')
        plantuml_block = re.compile(rf"(```{self.config.shortname}.+?```)",
                                     flags=re.DOTALL)
        plantuml_contents = re.compile(rf"```{self.config.shortname}(.+?)```",
                                     flags=re.DOTALL)
        documents = plantuml_block.findall(markdown)

        if documents:
            log.info(f'Found {len(documents)} plantuml block(s) in {page.file.src_path}')

        for document in documents:
            with tempfile.TemporaryDirectory() as temp:
                plantuml = plantuml_contents.findall(document)[0]
                plantuml = plantuml.split("\n")
                plantuml.insert(2, f'skinparam backgroundcolor {self.config.background_colour}')
                plantuml = "\n".join(plantuml)
                puml_path = join(temp, 'diagram.puml')
                self._write_file(puml_path, plantuml)

                subprocess.run(f'java -jar {dirname(__file__)}/plantuml.jar {puml_path} -tsvg',
                               shell=True)

                svg_path = join(temp, next(file for file in listdir(temp) if file.endswith('.svg')))
                svg = self._read_file(svg_path)
                svg = svg.replace('<?xml version="1.0" encoding="us-ascii" standalone="no"?>', '')
                markdown = markdown.replace(document, svg)

        return markdown

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
