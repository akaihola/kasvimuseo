# AGENTS.md

For every agent and every person who writes text in this repository. It decides
how we write, and how the issue backlog stays filled. It does not describe the
software: `docs/index.rst` does that, and `docs/issues/next.rst` is where you go
to pick up work.

This file is the only source for the rules below. State a rule here once. In any
other file, name this file instead of restating it.

## How to write here

The reader is a junior developer, or an agent with no memory of yesterday.
Neither can ask you a follow-up question. Write so that neither has to.

The rules come from
[ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/), a
controlled language built so that a technician cannot misread an instruction.
A [public summary of its rule categories](https://github.com/danyuchn/asd-ste100-skill/blob/master/references/writing-rules.md)
is enough to work from; this file lists the rules we apply.

- Use the active voice. Say who does the thing.
- Use simple tenses. Write "we removed it", not "it has been removed".
- Give one instruction per sentence.
- Keep an instruction to 20 words. Keep a description to 25 words.
- Keep a paragraph to one topic and six sentences.
- Use a list for three or more steps or conditions.
- Use one word for one meaning. Pick `check` or `verify`, then keep it.
- Keep a noun cluster to three words.
- Do not drop a subject, a verb or an article to make a sentence shorter.
- Define a term the first time you use it, or link to where it is defined.

Every document opens with one lead paragraph: who it is for, and what it
decides. The commands or the checklist come first. The argument comes below.

These rules bind new text and text you edit. They do not oblige you to rewrite a
document you are not otherwise touching.

## Maintain agent memories

Every agent must maintain the shared memories in `.agents/memory/`.

At the start of a session, every agent must read `.agents/memory/MEMORY.md`.
During a session, every agent must record durable project facts in that directory.
At the end of a session, every agent must update `MEMORY.md` when the memory index needs a new entry.

Use one Markdown file for each durable fact. Keep each file short and link it from `MEMORY.md`.
Do not write project memories in an agent-specific directory.

## Do not duplicate prose

Write a fact once, in the file that owns it. Everywhere else, write one short
sentence and name where the fact lives:

- a document — the path and the heading, or a Sphinx `:doc:` role;
- text that was removed — `docs/archive.rst`, which names the commit that still
  holds it;
- a decision — the commit subject, or the issue's `:Decision:` field.

This is the convention the [AGENTS.md standard](https://agents.md/) asks for:
one file states a rule, and every other file points at it.

A second copy is allowed only when a machine makes it. `docs/issues/next.rst` is
generated from the issue files, so it cannot disagree with them. A copy you type
can.

One exception, and it is deliberate: a build failure message says what to do
inline. An error that makes the reader open another file is bad to use, and that
costs more than the repeated sentence saves.

## What an agent writes at the end of a session

Do not paste the content of the files you edited. The reviewer reads the diff.

Write instead:

1. What changed for the person who uses the software.
2. What changed for the person who works on it.
3. The path, and the heading, of each thing you changed.
4. What is still open, and who owes it.

## The issue backlog

The register is `docs/issues/`. Its conventions, its metadata fields and its
build checks are in `docs/issues/README.rst`. Read `docs/issues/next.rst` to
pick up work.

### Reports arrive in `incoming.rst`

`docs/issues/incoming.rst` holds reports that wait, and nothing else. A report
leaves that page when it becomes a numbered issue file, and it leaves in the
same commit that creates the file. A report that earns no fix still becomes a
file, closed `Rejected` with the reasoning in `:Resolution:`. Do not write the
history of a report that left. Git holds it.

### Refill the backlog before it empties

Count the work that is free to start. The `Ready now` table of
`docs/issues/next.rst` is generated, so the source file shows a directive and no
rows. Count one of these two ways:

- cheap and approximate: count the issue files whose `:Status:` is `Open` or
  `Accepted` and that carry no `:Claimed:` field. An unmet dependency can still
  hold one of them back, so this is an upper bound;
- exact: build the documentation and read the rendered `Ready now` table.

When fewer than three are free, file new issues before you do anything else.
Take the first source that has an item:

1. `docs/issues/incoming.rst`, section `Waiting` — a person wrote it, so it
   outranks the plans.
2. `docs/test-coverage-plan.rst`, section `Work packages`, in the order that
   its `Sequencing` section gives.
3. `docs/upgrade-plan.rst` — the lowest-numbered stage that is not done.

For each item:

1. Write `docs/issues/NNN-<slug>.rst`. Give it every field that
   `docs/issues/README.rst` defines under "Metadata fields". Set
   `:Status: Open` and `:Decision: undecided`.
2. Add its `issue-rank` line to `docs/issues/index.rst`. The documentation
   build fails when an issue file has no ranking entry.
3. When the item came from `incoming.rst`, delete the report there in the same
   commit.
4. Run the documentation build. `docs/issues/next.rst` says how.

The issue file is the source. A task description carries one paragraph and the
path of the issue file. It does not carry a copy of the issue.
