---
name: running-ansible-from-this-checkout
description: "How to run ansible-playbook here — no ansible on the host, uvx plus four env vars, and sandbox off for a real local run"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5bd34fbb-9648-4fa7-b77c-4ec6ab9102b8
  modified: 2026-08-08T09:18:48.874Z
---

Nothing on this machine has `ansible`. Run it with
`uvx --from ansible ansible-playbook` (the full package: `install.yaml` uses
`django_manage`, which is `community.general`; plain `ansible-core` fails the
syntax check on it). Four environment variables are needed, because every
default path ansible writes to is read-only:

    UV_TOOL_DIR=$TMPDIR/uvtools UV_TOOL_BIN_DIR=$TMPDIR/uvbin
    ANSIBLE_LOCAL_TEMP=$TMPDIR/ansible-tmp ANSIBLE_HOME=$TMPDIR/ansible-home

`ansible.cfg` names `ansible/get-vault-password.sh`, so set
`ANSIBLE_VAULT_PASS=anything` even for `--syntax-check`; with a made-up
one-host inventory nothing vaulted is decrypted. Syntax-check then passes with
only the vendored `nginxinc.nginx` deprecation warnings.

Actually *running* a playbook locally needs the Bash sandbox off — ansible-core
2.21 starts a local RPC server over a Unix socket and the sandbox refuses it —
and `executable: /bin/bash` has to become
`/run/current-system/sw/bin/bash`, since NixOS has no `/bin/bash`. Both are
host artefacts, not repository problems. Rehearsing a play task this way, with
its paths pointed at a temp directory, is the only evidence available for
anything under `ansible/`: see [[no-ssh-to-production]].

`openssl` is not on the host either; `nix-shell -p openssl` gets it, also with
the sandbox off.
