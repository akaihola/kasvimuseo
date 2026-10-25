# Run the suite in the container

This note helps contributors select the supported test environment.

Read [README.rst](../../README.rst), "Development setup", for prerequisites.
Run these commands from the checkout:

```bash
dev/kasvimuseo app test
dev/kasvimuseo app browser-test
dev/kasvimuseo docs --clean
```

On NixOS, run them in a Nix shell with the PostgreSQL tools, from a checkout with a short path: see [README.rst](../../README.rst), "Testing", the paragraph that starts "On NixOS".

The helper runs application tests inside the development image with a temporary PostgreSQL database.
Browser tests run on the host against the container application.
Read [README.rst](../../README.rst), "Continuous integration", for browser installation and check details.
