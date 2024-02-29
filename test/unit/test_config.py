from mkdocs_plantuml_local.config import MkDocsPluginPlantUMLLocalConfig


def test_mkdocs_configuration_defaults():
    config = MkDocsPluginPlantUMLLocalConfig()

    # parameters: with defaults
    assert config.cache is False
    assert config.shortname == 'plantuml'
    assert config.background_colour == 'transparent'

    # parameters: optional
    assert config.class_name is None
