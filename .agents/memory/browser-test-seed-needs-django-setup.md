---
name: browser-test-seed-needs-django-setup
description: "The browser seed imports Django models before calling django.setup under the current Django 2 image"
metadata:
  node_type: memory
  type: project
---

With the Django 2 development image, `dev/kasvimuseo app browser-test` fails
while loading `browser_tests/seed.py`: it imports Django models before the
`django.setup()` call at the bottom of the file. A temporary call after
`import django` allowed the issue 080 browser check to run; the tracked seed
file remains unchanged. Fix the seed ordering before relying on this command.
