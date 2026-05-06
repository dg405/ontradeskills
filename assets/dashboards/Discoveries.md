---
type: dashboard
---

# Discoveries

Venue stubs created by `/discover`. Promote by filling out the venue note and removing the `discovered` tag.

```dataview
TABLE city, tier, file.ctime AS "Discovered"
FROM "Venues"
WHERE contains(tags, "discovered")
SORT file.ctime DESC
```
