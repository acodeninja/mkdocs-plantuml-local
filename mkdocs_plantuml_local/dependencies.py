import mkdocs.exceptions
import shutil

DEPENDENCIES = ['dot', 'java']


def check_dependencies():
    checked_dependencies = {d: shutil.which(d) for d in DEPENDENCIES}
    if None in checked_dependencies.values():
        missing = [d for d, r in checked_dependencies.items() if r is None]
        raise mkdocs.exceptions.PluginError('Missing dependencies: {}'.format(", ".join(missing)))
