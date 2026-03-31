# Packaging Intelligence Engine — Paryaveksha

> A data-driven decision layer for sustainable packaging evaluation, built on top of Open Food Facts.

**GSoC 2026 Proposal | Open Food Facts | Tejaswini Pinnamreddy**

---

## Overview

Open Food Facts already collects packaging data. This project adds the **intelligence layer** on top of it — scoring packaging options by recyclability, carbon footprint, material efficiency, and cost.

---

## Scoring Formula

```
PackagingScore = (0.35 * recyclability_index)
               + (0.30 * carbon_footprint_score)
               + (0.20 * size_efficiency_score)
               + (0.15 * cost_efficiency_score)
```

All values normalized to `[0, 1]`. Weights configurable per request.
Modes: `balanced`, `environment-first`, `cost-sensitive`

---

## Example

**Input:**
```json
{ "weight_kg": 0.5, "fragile": true, "is_liquid": true }
```

**Output:**
```json
[
  { "name": "Recycled Glass Bottle",  "score": 0.82, "rank": 1 },
  { "name": "Molded Pulp Insert",     "score": 0.74, "rank": 2 },
  { "name": "Recycled Cardboard Box", "score": 0.68, "rank": 3 }
]
```
> `Plastic Wrap` filtered out — `liquid_safe: false`

---

## Repository Structure

```
├── decision_engine/
│   └── scoring.py          <- Core scoring + constraint logic
├── data/
│   └── packaging_options.json  <- Sample packaging dataset
├── docs/
│   └── proposal.md         <- Full GSoC 2026 proposal
└── README.md
```

---

## Author

**Tejaswini Pinnamreddy** — GSoC 2026 Applicant | Open Food Facts
tejaswini.pr.it@gmail.com | Hyderabad, India (UTC +5:30)
