---
type: dashboard
---

# Pipeline

Venues with products in the sales pipeline (not yet listed).

```dataview
TABLE pipeline_products AS "Pipeline", tier, last_visited
FROM "Venues"
WHERE type = "venue" AND length(pipeline_products) > 0
SORT last_visited DESC
```
