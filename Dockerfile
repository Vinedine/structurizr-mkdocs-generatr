FROM python:3.12-slim

ARG STRUCTURIZR_CLI_VERSION=2025.11.09
ARG PLANTUML_VERSION=1.2026.2

# Java runtime (Structurizr CLI + PlantUML), Graphviz (PlantUML needs it), wget/unzip for downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jre-headless graphviz wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Structurizr CLI vNext (distributed as a zip containing lib/ + bin/)
RUN wget -q "https://github.com/structurizr/cli/releases/download/v${STRUCTURIZR_CLI_VERSION}/structurizr-cli.zip" \
        -O /tmp/structurizr-cli.zip && \
    unzip -q /tmp/structurizr-cli.zip -d /opt/structurizr-cli && \
    chmod +x /opt/structurizr-cli/structurizr.sh && \
    rm /tmp/structurizr-cli.zip

# PlantUML (MIT-licensed standalone JAR)
RUN wget -q "https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-mit-${PLANTUML_VERSION}.jar" \
        -O /opt/plantuml.jar

# Install the Python CLI
COPY . /app
RUN pip install --no-cache-dir /app && rm -rf /app

# Verify tools are accessible
RUN /opt/structurizr-cli/structurizr.sh version && \
    java -jar /opt/plantuml.jar -version

ENV STRUCTURIZR_MKDOCS_DOCKER=1

WORKDIR /var/model
ENTRYPOINT ["structurizr-mkdocs"]
