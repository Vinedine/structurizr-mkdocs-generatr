!!! note "For Documentation Authors"

    This page shows the markup features available when writing pages for your architecture site. The site is built with [MkDocs Material](https://squidfunnel.github.io/mkdocs-material/) and supports standard [Markdown syntax](https://www.markdownguide.org/basic-syntax/).

## C4 Diagrams

Diagrams defined in the workspace can be embedded using the `embed:` syntax:

```markdown
![System Landscape Diagram](embed:SystemLandscape)
```

![System Landscape Diagram](embed:SystemLandscape)

See also: <https://www.structurizr.com/help/documentation/diagrams>

## Images

Static assets can be included using standard Markdown image syntax. Place images in the assets directory and reference them with absolute paths:

```markdown
![Leading with Capabilities](/img/leading-with-capabilities.jpg)
```

![Leading with Capabilities](/img/leading-with-capabilities.jpg)

## PlantUML Diagrams

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

## Mermaid Diagrams

[Mermaid.js](https://mermaid.js.org/intro/#diagram-types) diagrams are supported natively by MkDocs Material:

````markdown
```mermaid
graph TD;
  A-->B;
  A-->C;
  B-->D;
  C-->D;
```
````

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
