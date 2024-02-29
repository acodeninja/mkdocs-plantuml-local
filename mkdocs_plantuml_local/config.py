import mkdocs.config
import mkdocs.config.config_options


class MkDocsPluginPlantUMLLocalConfig(mkdocs.config.base.Config):
    shortname = mkdocs.config.config_options.Type(str, default="plantuml")
    background_colour = mkdocs.config.config_options.Type(str, default="transparent")
    cache = mkdocs.config.config_options.Type(bool, default=False)
    class_name = mkdocs.config.config_options.Optional(
        mkdocs.config.config_options.Type(str, default=None),
    )
