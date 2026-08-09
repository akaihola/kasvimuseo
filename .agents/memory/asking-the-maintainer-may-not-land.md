---
name: asking-the-maintainer-may-not-land
description: ask_user_question_kandev may never return an answer; record the ruling in the issue file instead of blocking
metadata: 
  node_type: memory
  type: project
  originSessionId: 95597124-5f69-4016-be00-a081bd2d3e40
  modified: 2026-08-09T14:58:15.401Z
---

`ask_user_question_kandev` went unanswered through five attempts while settling
issue 032 on 2026-08-01 — three rejections and two `socket connection was
closed unexpectedly` errors, with no explanation and the task prompt re-sent
verbatim each time. The **sixth** landed and was answered. The ones that failed
were long: three questions, multi-paragraph `context`. The one that worked was
a single question with four options and the evidence compressed into the
prompt.

**Why:** many kasvimuseo issues carry `:Decision: undecided`, and the task
wording ("come to the maintainer with an answer rather than a survey") makes
asking sound like a gate. It is not one — blocking on it delivers nothing.

It does sometimes land: settling issue 053 the same day, the first call was
rejected and a second, shorter one — a single question, four options, evidence
in `context` — was answered. So a rejection is worth exactly one retry in a
tighter shape, and no more. **Ask small from the start**: one question, few
options, the evidence compressed. Both the answers that arrived had that shape
and none of the long ones did.

The "ask small" rule is weaker than the 032 sample suggested. On 2026-08-03,
finalizing 063, a **two**-question call with four options each and a long
`context` was answered immediately and on the first try. What that call had
going for it was not brevity but that the session was one the user had just
started for this purpose. So: shape matters less than whether anyone is
watching. Ask in the shape the question actually needs.

**An answer that arrives after the issue is merged is not too late, and may be
worth more than a confirmation.** 063 had been merged as `Accepted` recording
"asked, no answer". The answers then eliminated *both* of the candidates the
file had ranked first, leaving none of its three standing — a better outcome
than confirming one, but only if the file is actually revisited. Re-ask on any
task that inherits an issue whose `:Decision:` says no answer came, and when
one lands, fix every place the file claims otherwise (`:Decision:`, `:Evidence:`,
the `incoming.rst` narrative and the `index.rst` ranking paragraph all repeat
it), annotating the superseded analysis rather than rewriting it to look like it
had known.

Keep working while it is outstanding. In 032 the answer arrived after the work
was committed, and applying it cost one commit — the ruling changed prose, not
code, because the recommendation and the ruling agreed. Blocking would have
bought nothing.

Confirmed again on 2026-08-04 settling 062: two calls, both two questions with
three or four options, both refused by the harness within a second in an
unattended run. That is a refusal at the transport, not a maintainer declining
— so it says nothing about the question and is not worth reshaping.

Confirmed again on 2026-08-09 on the 070 rehearsal task: two identical
single-question calls, both `socket connection was closed unexpectedly` within
a second, the task prompt re-sent verbatim after each. Ruled on the evidence,
recorded the attempt in 070's `:Resolution:`, and left the issue `Accepted`.

**The late answer can reverse the evidence-based ruling, not just confirm it.**
Settling 066 on 2026-08-04: two calls failed (one socket error, one harness
refusal), so I ruled on the evidence for the *reversible* option — wiring
`EMAIL_*` from the environment — and committed it with the issue `Accepted`.
The answer then arrived and chose the **destructive** option instead (delete
the `mail_admins` handler, close `Rejected`), which made the whole
implementation dead code: with no handler, nothing read those settings. Cost
was two commits withdrawn, not prose.

So when an issue's options split into reversible and destructive, and the task
says not to take the destructive one unmerged without a ruling, expect the
ruling to be able to pick it anyway. Keep the interim work on its own branch or
a tag (`git tag interim-<slug>` before `git reset --hard master`) rather than
merged, so withdrawing it is one command and the issue file can point at the
tag instead of carrying settings nothing reads. Rebuilding the branch cleanly
beats landing "add X" then "remove X" on `master`.

**Never let the card order disagree with the options' own numbers.** Settling
062 on 2026-08-04 I listed the issue's three options with my recommendation
first, so card 2 was labelled "Option 1: wait for the iPad". The answer came
back `q1_opt2` and I read it as option 2 — arguing it from the *other* answer,
which was self-consistent and wrong. Re-asking with two cards whose labels
carried no numbers at all got the same answer as the first time: option 1, and
the fix I had built and merged came out again. Either keep the cards in the
options' numeric order or strip the numbers from the labels, and when an answer
is ambiguous, re-ask rather than reasoning from a second answer — an ambiguous
`opt<N>` id is not evidence about intent.

**How to apply:** try the question once, briefly. If it does not land, do the
work on the evidence and say so *in the issue file's* `:Decision:` field —
"Recorded rather than ruled: the question was put to the maintainer and no
answer came back, so this is what the evidence supports" — plus what a later
ruling could still cheaply change. Then state the same in the final message.
Do not retry the tool repeatedly; a declined call is not a transport error to
work around. See [[resolution-hash-dies-in-the-rebase]] for the other issue-file
field that needs care, and [[two-syntax-traps-django15-and-docinfo]] for the
docinfo blank-line trap that would hide a `:Decision:` written this way.
