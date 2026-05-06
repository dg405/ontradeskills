---
type: dashboard
---

# Menu opportunities

Latest menu analyses across the venue book. Each row links to the venue note where the dated `## Menu analysis` block lives.

```dataview
TABLE WITHOUT ID file.link AS "Venue", last_menu_fetch AS "Fetch tier", last_visited
FROM "Venues"
WHERE type = "venue" AND last_menu_fetch
SORT last_visited DESC
```
