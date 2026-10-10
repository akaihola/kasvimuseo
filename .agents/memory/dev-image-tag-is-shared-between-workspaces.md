# Use separate development image tags

This note helps contributors prevent concurrent worktrees from replacing each other's development image.

Set a distinct image tag before building and testing:

```bash
export KASVIMUSEO_IMAGE=kasvimuseo-dev-task-name
dev/kasvimuseo app build
dev/kasvimuseo app test
```

Replace `task-name` with your task identifier.
Keep the variable set for every helper command that uses this image.
The default `kasvimuseo-dev` tag belongs to the container storage, rather than to one checkout.
If installed packages differ from the checkout's requirements, rebuild the selected image before diagnosing application code.
