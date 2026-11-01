# Feature Brief — Task Comments

This is the **plain-English request** you feed to `/speckit.specify` in Lab 01.
It is intentionally informal and slightly under-specified — turning it into an
unambiguous, testable specification is the work of Module 04. Do **not** add
implementation detail here; that is what `/speckit.plan` is for.

---

## The ask (as a product owner would phrase it)

Engineers want to discuss a task without leaving the board. Add a lightweight
**comment thread** to each task.

- On the board, each task card shows a small **comment count** (e.g. 💬 3). It's
  hidden when there are no comments.
- Clicking it expands an inline **thread** under the card: the existing comments,
  oldest at the top, each showing who wrote it and roughly when.
- Below the thread is a small form: an **author** field and a **comment** box,
  and a "Post" button.
- You can **delete** a comment you no longer want. (For now, anyone can delete
  any comment — no auth in this app yet.)
- Comments are plain text. Keep them short — a sentence or two, not essays.
- A comment can't be posted without both an author and some text.
- Deleting a task should take its comments with it.

## Out of scope (for this feature)

- Editing a comment after posting.
- Replies / threading / reactions / @-mentions.
- Rich text, attachments, or Markdown rendering.
- Any authentication or "who am I" — the author is just typed in.
- Notifications.

## Notes the team already knows (constraints the spec must honour)

- This app owns its schema in one file, `database/schema.sql`. A new table is
  fine — but it goes there, as a reviewed change. No migration tooling.
- Every backend (.NET, Python, Java) must expose the feature identically and
  return byte-identical JSON for the same request (timestamp key casing aside).
- The existing error contract is `404` for a missing resource, `422` for a bad
  request body. New endpoints follow it.
- New behaviour ships with tests in the same layer.

## Open questions the spec should resolve (don't answer them here)

- What exactly is "short"? A hard character limit?
- What's the max length of an author name?
- What does `GET` return for a task that doesn't exist — `404`, or `200 []`?
- Is there a max number of comments per task?
- What's the response body of `POST` — the new comment, or the whole thread?
- Newest- or oldest-first in the API response?

`/speckit.clarify` will walk you through these.
