from os.path import dirname, join
from urllib.request import urlretrieve


def download_plantuml():
    print('Downloading PlantUML')
    urlretrieve('https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar',
                join(dirname(__file__), 'mkdocs_plantuml_local', 'plantuml.jar'))


if __name__ == "__main__":
    download_plantuml()
