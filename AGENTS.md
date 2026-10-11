# AGENTS.md

This file guides contributors and coding agents. It defines writing rules and points to the task workflow.

[TASKS.md](TASKS.md) tracks the work.

Read the rules at the bottom of `TASKS.md` before changing issue status.
Completed work stays unchecked until the user explicitly accepts it.
Tests and deployment are not acceptance.

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

A project memory must help any contributor on any machine with any agent.
A fact about one machine, one agent harness, or one sandbox is not a project memory.
Record such a fact in your agent's private memory.
Keep machine paths, session identifiers, and tool permissions out of `.agents/memory/`.

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

## Existing issue records

Existing issue records remain in `docs/issues/`.
Follow `docs/issues/README.rst` when editing their metadata or generated register.
Link relevant records from task descriptions instead of duplicating their contents.
Use `TASKS.md` for new proposals and work status.
