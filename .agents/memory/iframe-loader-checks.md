This note helps contributors find the iframe origin rule and its browser checks.

Read `README.rst`, "Embedding the species list", for the origin rule and the message rule.
`browser_tests/test_iframe_loader.py` checks the iframe address and the messages that the loader accepts.
It uses routed pages in both browser engines.
These tests need no application server or database.
Run them with the host pytest environment described in `browser_tests/requirements.txt`.
