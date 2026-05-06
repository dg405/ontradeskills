---
type: dashboard
---

# Expiring contracts (next 90 days)

```dataview
TABLE venue, distributor, end_date, value_gbp
FROM "Contracts"
WHERE type = "contract"
  AND status = "active"
  AND end_date
  AND date(end_date) <= date(today) + dur(90 days)
SORT end_date ASC
```
