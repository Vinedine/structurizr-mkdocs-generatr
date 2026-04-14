# 4. Build Unified Data Lakehouse

Date: 2025-05-20

## Status

Completed

## Context

BelFoot FC generates operational data across ticketing, merchandising, stadium operations, and sporting analytics. Business stakeholders need unified reporting and trend analysis, but data is siloed across individual system databases.

## Decision

Build a unified data lakehouse using Databricks on Azure with Unity Catalog for data governance. Azure Data Factory ETL pipelines ingest events from the Integration Platform and batch-load from operational databases. Power BI dashboards serve curated data products to business users.

![ContainerDataPlatform](embed:ContainerDataPlatform)

## Consequences

- Single source of truth for cross-departmental analytics and KPI reporting
- Self-service data exploration via Databricks notebooks for data analysts
- Unity Catalog enforces row-level security and data governance policies
- ETL pipeline maintenance required as source system schemas evolve
- Power BI dashboards provide executive and operational visibility
