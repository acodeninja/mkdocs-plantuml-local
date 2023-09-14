# MkDocs PlantUML Local

Render Plantuml codeblocks in mkdocs without sending sensitive diagrams to a public server.

## Configuration

**Minimal**

```yaml
plugins:
  - plantuml-local
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: plantuml
          class: plantuml
          format: !!python/name:pymdownx.superfences.fence_code_format
```

**All**

```yaml
plugins:
  - plantuml-local:
      # shortname is language used to identify 
      # blocks to process, defaults to `plantuml`
      shortname: puml
      # background_colour sets the background
      # fill colour used, defaults to `transparent`
      background_colour: white
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: puml
          class: puml
          format: !!python/name:pymdownx.superfences.fence_code_format
```

## Licence

This MkDocs plugin is licenced under the MIT license.

Plantuml is redistributed with this package, under the [GPL-3.0 license](https://github.com/plantuml/plantuml/blob/master/license.txt).
