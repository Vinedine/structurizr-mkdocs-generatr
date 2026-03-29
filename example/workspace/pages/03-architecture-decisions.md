## Decisions That Shape the Architecture

Every IT landscape is the result of decisions: which cloud to use, which ERP to adopt, how to handle integrations, where to invest in AI. Too often these decisions live in meeting notes, emails, or someone's memory. When the people who made them leave, the rationale is lost.

**Architecture Decision Records (ADRs)** solve this by documenting each strategic decision alongside the architecture itself -- in the same repository, reviewed through the same pull request process.

## What an ADR Captures

Each decision record follows a simple structure:

<div class="grid cards" markdown>

- :material-help-circle-outline: **Context**

    ---

    Why was a decision needed? What problem or opportunity triggered it?

- :material-check-circle-outline: **Decision**

    ---

    What was decided, and what alternatives were considered?

- :material-alert-circle-outline: **Consequences**

    ---

    What are the trade-offs? What becomes easier, and what becomes harder?

- :material-tag-outline: **Status**

    ---

    Is this decision pending, accepted, completed, or superseded by a later one?

</div>

## ADRs and the Branching Model

One of the most powerful features of Architecture as Code is that **architecture changes follow the same Git workflow as application code**:

```mermaid
flowchart LR
    ADR["Write ADR"] --> BR["Create Branch"]
    BR --> MOD["Model Changes"]
    MOD --> VAL["Validate Locally"]
    VAL --> PR["Pull Request"]
    PR --> REV["Peer Review"]
    REV --> MRG["Merge to Main"]
    MRG --> DEP["Auto-Deploy Site"]

    style ADR fill:#4CAF50,color:#fff
    style BR fill:#2196F3,color:#fff
    style MRG fill:#FF9800,color:#fff
```

This means you can:

- **Create a branch for a future architecture change** -- model the new systems, containers, and deployment infrastructure before anything is built
- **Link the branch to an ADR** -- the decision record explains *why* the change is happening, the branch shows *what* the architecture will look like
- **Review the full impact** -- the pull request shows exactly which systems, deployments, and business capabilities are affected
- **Merge when approved** -- once the decision is accepted and the architecture validated, merge into main and the site updates automatically

!!! example "Example: Cashless Stadium Decision"

    ADR-0006 documents the decision to implement a cashless-only policy at BelFoot Arena. The branch for this decision included:

    - A new **Cashless Payment** software system with its containers (Payment Gateway, NFC Terminal Manager, Digital Wallet Service)
    - Updated **deployment views** showing NFC terminals in the stadium data center
    - New **cross-context links** between Fan Experience, Financial Operations, and Marketing & Sales
    - Updated **capability maps** reflecting the new "Process Cashless Payments" business capability

    All of this was reviewed in a single pull request, with the ADR providing the business rationale and the model changes showing the technical impact.

## Living History

Because ADRs are version-controlled alongside the architecture, they form a **living history** of how the IT landscape evolved:

- **Trace any system back to the decision that created it** -- why was SAP S/4HANA chosen as the ERP? See ADR-0002.
- **Understand superseded decisions** -- when a decision is replaced, the old ADR links to the new one, preserving the full chain of reasoning
- **Audit trail for compliance** -- every decision has a date, a status, and a full Git history of who approved it and when

Browse the **Architecture Decision Records** tab in the top navigation to see the decisions that shaped BelFoot FC's IT landscape.
