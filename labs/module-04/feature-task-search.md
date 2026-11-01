# Feature Brief — Task Search

This is the **plain-English request** you feed to the specify step (`/speckit.specify`,
or `/speckit-specify` in skills mode) in Lab 01. It is intentionally informal and
slightly under-specified — turning it into an unambiguous, testable specification
is the work of Module 04. Do **not** add implementation detail here; that is what
the plan step is for.

> The previous brief (task comments) is kept as
> [`comment-feature-brief.md`](comment-feature-brief.md).

---

## The ask (as a product owner would phrase it)

Engineers want to find a task without scanning every column. Add a keyword
**search** to the board.

- A **search box** sits next to the existing status filter.
- As the engineer types a word or phrase, the board narrows to the tasks that
  match. The count on each column reflects only the tasks that match.
- A task matches when its **title or description** contains what was typed.
  Upper/lower case doesn't matter.
- Search and the **status filter work together** — a task has to satisfy both.
- Clearing the box (or a small "clear" control) brings the full board back.
- When nothing matches, the board says so clearly — it must look different from
  an empty board or an empty column.
- The board never shows results for something other than what is currently in
  the box, even if the engineer types quickly.
- A box that is empty or only spaces means "no search" — not an error.

## Out of scope (for this feature)

- Searching comment text.
- Ranking, fuzzy matching, typo tolerance, or highlighting the matched text.
- Saved, shared, or bookmarkable searches; remembering a search between visits.
- Advanced syntax (quotes, AND/OR, `assignee:ana`).
- Pagination or sorting.
- Any change to what a task contains or to the database schema.

## Notes the team already knows (constraints the spec must honour)

- Search belongs in the existing layers. The React app keeps `components/` →
  `pages/` → `services/`, with all HTTP in `services/`. Each backend keeps
  Controller/Router → Service → Repository, with all database access in the
  repository.
- Every backend (.NET, Python, Java) must give the **same results, in the same
  order, with the same status codes** for the same request. The task shape does
  not change (timestamp key casing aside).
- Anything the user types is just text. Characters like `%`, `_`, `\` and `'`
  must not change what the query means or cause an error.
- With no search, the board and the existing task list behave exactly as today.
- The existing error contract is `404` for a missing resource, `422` for a bad
  request. New behaviour follows it.
- New behaviour ships with tests in the same layer, in every backend and in the
  frontend.

## Open questions the spec should resolve (don't answer them here)

- Should **assignee** be searched too, or only title and description?
- Is a multi-word search one exact phrase, or must every word appear anywhere?
- Is there a maximum query length? What happens when it's exceeded?
- Is there a minimum length — does a single letter count?
- Is leading/trailing whitespace ignored?
- Does search run as the user types (and how soon after they stop), or only on
  Enter / a Search button?
- What does the API return when nothing matches — `200 []` or `404`?
- Is the filtering done by the server or in the browser?
- Does the **Refresh** control keep the current search?
- What exactly does the "nothing matches" message say, and can the user clear
  the search from it?

The clarify step (`/speckit.clarify`, or `/speckit-clarify`) will walk you
through these.
