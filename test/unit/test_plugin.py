import mkdocs.exceptions
import pytest
import json
from unittest.mock import patch, call, ANY


@patch('mkdocs_plantuml_local.plugin.check_dependencies')
def test_on_config_with_no_missing_dependencies(check_dependencies, plugin_factory):
    plugin = plugin_factory()
    plugin.on_config(plugin.config)


@patch('mkdocs_plantuml_local.plugin.check_dependencies',
       side_effect=mkdocs.exceptions.PluginError(""))
def test_on_config_with_missing_dependencies(check_dependencies, plugin_factory):
    plugin = plugin_factory()
    with pytest.raises(mkdocs.exceptions.PluginError):
        plugin.on_config(plugin.config)


@patch('mkdocs_plantuml_local.plugin.render')
@patch('mkdocs_plantuml_local.plugin.time.time', return_value=1709215168.65)
@patch('mkdocs_plantuml_local.plugin.get_cache', return_value=None)
@patch('mkdocs_plantuml_local.plugin.put_cache')
def test_on_post_page_without_cache(put_cache,
                                    get_cache,
                                    time,
                                    render,
                                    plugin_factory,
                                    setup_fixtures,
                                    mock_page,
                                    mock_logger):
    render.return_value = setup_fixtures.joinpath("rendered_sample.svg").read_text()
    plugin = plugin_factory()

    rendered_page = plugin.on_post_page(
        setup_fixtures.joinpath('on_post_page_input.html').read_text(),
        page=mock_page,
        config=plugin.config,
    )

    mock_logger.info.assert_has_calls([call("Rendering diagram 1 of page file"),
                                       call("Handled diagram 1 of page file in 0.0ms")])

    get_cache.assert_called_once_with(json.dumps(list(plugin.config.values())), 'file', ANY)
    put_cache.assert_called_once_with(ANY, json.dumps(list(plugin.config.values())), 'file', ANY)

    assert (rendered_page.strip() ==
            setup_fixtures.joinpath("on_post_page_output.html").read_text().strip())


@patch('mkdocs_plantuml_local.plugin.render')
@patch('mkdocs_plantuml_local.plugin.time.time', return_value=1709215168.65)
@patch('mkdocs_plantuml_local.plugin.get_cache')
@patch('mkdocs_plantuml_local.plugin.put_cache')
def test_on_post_page_without_cache(put_cache,
                                    get_cache,
                                    time,
                                    render,
                                    plugin_factory,
                                    setup_fixtures,
                                    mock_page,
                                    mock_logger):
    get_cache.return_value = setup_fixtures.joinpath("rendered_sample.svg").read_text()
    plugin = plugin_factory()

    rendered_page = plugin.on_post_page(
        setup_fixtures.joinpath('on_post_page_input.html').read_text(),
        page=mock_page,
        config=plugin.config,
    )

    mock_logger.info.assert_has_calls([call("Using cache for diagram 1 of page file"),
                                       call("Handled diagram 1 of page file in 0.0ms")])

    get_cache.assert_called_once_with(json.dumps(list(plugin.config.values())), 'file', ANY)
    put_cache.assert_not_called()
    render.assert_not_called()

    assert (rendered_page.strip() ==
            setup_fixtures.joinpath("on_post_page_output.html").read_text().strip())
