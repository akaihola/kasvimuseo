Issue 078: Planting photo text reads a missing attribute
============================================================

:Status: Open
:Claimed: KAN fc7b0c9c-41cb-4ef6-9d3e-4a8f47816206
:Severity: Low
:Area: models / text
:Reported: 2026-09-05
:Source: Stage 10 source inspection
:Evidence: ``PlantingPhoto.__unicode__`` reads ``self.observation``, but the model has no such attribute.
:Depends on: (none)
:Blocks: 077 -- finish this method before the interpreter transition
:Related: 036 -- the runtime upgrade programme
:Decision: undecided
:Resolution: (none yet)

Work
----

This issue is for the implementation agent. It tracks a defect outside issue 076's source preparation.

The text method references a missing attribute and can raise ``AttributeError``.
The model has a ``planting`` field, whose related model has an ``observation`` field.

#. Choose the intended photo label from the model's existing data.
#. Add a regression test for a normal ``PlantingPhoto`` instance.
#. Repair the text method and prepare it for Python 3.
