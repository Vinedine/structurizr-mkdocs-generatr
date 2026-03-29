# 2. Select SAP S4HANA as ERP

Date: 2025-03-01

## Status

Completed

## Context

BelFoot FC needs a centralized ERP system to manage finance, procurement, inventory, and HR payroll. Multiple departments currently use disconnected spreadsheets and legacy tools for financial operations.

## Decision

Adopt SAP S4HANA as the enterprise ERP platform, centralizing financial accounting, accounts payable/receivable, procurement, inventory management, and payroll processing.

![ContainerSapS4Hana](embed:ContainerSapS4Hana)

## Consequences

- All financial data consolidated in a single system of record
- HR Portal and Logistics Planner integrate via SAP OData APIs for payroll and purchase order sync
- Significant licensing and implementation investment
- Staff require SAP Fiori training for self-service operations
