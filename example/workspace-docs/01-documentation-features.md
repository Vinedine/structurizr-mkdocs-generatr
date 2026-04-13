This page showcases the features available when writing documentation for the generated site. The site is built with [MkDocs Material](https://squidfunnel.github.io/mkdocs-material/) and supports standard [Markdown syntax](https://www.markdownguide.org/basic-syntax/).

### Embedding diagrams

Diagrams defined in the workspace can be embedded using the `embed:` syntax:

```markdown
![System Landscape Diagram](embed:SystemLandscape)
```

![System Landscape Diagram](embed:SystemLandscape)

See also: <https://www.structurizr.com/help/documentation/diagrams>

### Embedding images

Static assets can be included using standard Markdown image syntax. Place images in the assets directory and reference them with absolute paths:

```markdown
![A nice picture](/pictures/nice-picture.png)
```

[Sun](https://www.flickr.com/photos/schmollmolch/4937297813/), by Christian Scheja

![A nice picture](/pictures/nice-picture.png)

### PlantUML

PlantUML can be embedded directly in Markdown files and will be rendered as SVG diagrams:

````markdown
```puml
@startuml
Foo -> Bar: doSomething()
@enduml
```
````

```puml
@startuml
Foo -> Bar: doSomething()
@enduml
```

### Mermaid diagrams

[Mermaid.js](https://mermaid.js.org/intro/#diagram-types) diagrams are supported natively by MkDocs Material.

```mermaid
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
```

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

### Admonitions

!!! note
    This is a note admonition.

!!! warning
    This is a warning admonition.

!!! tip "Custom title"
    Admonitions can have custom titles.

??? example "Click to expand"
    Collapsible admonitions are also supported.

