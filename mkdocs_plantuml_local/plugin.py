import json
import time

import mkdocs.plugins
from lxml import etree
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

import mkdocs_plantuml_local.logging
from mkdocs_plantuml_local.caching import get_cache
from mkdocs_plantuml_local.caching import put_cache
from mkdocs_plantuml_local.config import MkDocsPluginPlantUMLLocalConfig
from mkdocs_plantuml_local.dependencies import check_dependencies
from mkdocs_plantuml_local.render import render

get_plugin_logger = getattr(mkdocs.plugins,
                            "get_plugin_logger",
                            mkdocs_plantuml_local.logging.get_plugin_logger)


class MkDocsPluginPlantUMLLocal(
    mkdocs.plugins.BasePlugin[MkDocsPluginPlantUMLLocalConfig]
):
    def __init__(self):
        self.logger = get_plugin_logger(__name__)

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        check_dependencies()
        return config

    def on_post_page(
        self, output: str, *, page: Page, config: MkDocsConfig
    ) -> str | None:
        html = etree.HTML(output)

        for index, block in enumerate(html.cssselect(f"pre.{self.config.shortname}")):
            start_time = time.time() * 1000

            plantuml_code = "".join(block.cssselect("code")[0].itertext())
            plantuml_code = self._pre_render(plantuml_code)

            cache_keys = [
                json.dumps(list(self.config.values())),
                page.file.src_path,
                plantuml_code,
            ]

            svg = get_cache(*cache_keys)

            if not svg:
                self.logger.info(
                    f"Rendering diagram {index + 1} of page {page.file.src_path}"
                )
                svg = render(plantuml_code)
                put_cache(svg, *cache_keys)
            else:
                self.logger.info(
                    f"Using cache for diagram {index + 1} of page {page.file.src_path}"
                )

            svg = etree.XML(svg.encode("utf-8"))
            svg = self._post_render(svg)

            block.getparent().replace(block, svg)
            end_time = time.time() * 1000
            self.logger.info(
                f"Handled diagram {index + 1} of page {page.file.src_path} in {end_time - start_time}ms"
            )

        return etree.tostring(html, encoding=str, method="html")

    def _pre_render(self, plantuml):
        plantuml = plantuml.split("\n")
        try:
            plantuml.insert(
                plantuml.index("@enduml"),
                f"skinparam backgroundcolor {self.config.background_colour}",
            )
        except ValueError:
            self.logger.warning(
                "Diagram does not contain UML, skipping set "
                f"{self.config.background_colour} background"
            )
        return "\n".join(plantuml)

    def _post_render(self, svg):
        svg.attrib["preserveAspectRatio"] = "xMidYMid"
        svg.attrib["style"] = "width: auto; height: auto;"

        if self.config.class_name:
            svg.attrib["class"] = self.config.class_name

        return svg
