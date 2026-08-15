---
name: lead-1-is-the-staging-rehearsal-host
description: "The 070 rehearsal host lives on (Hetzner CX11, Debian 10); secrets and the exact ansible invocation are in the base checkout's .dev/rehearsal"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ffdd050-57e8-4227-a77a-c59056215558
  modified: 2026-08-09T20:01:13.205Z
---

The issue 070 **reduced** rehearsal passed on 2026-08-09 (commit 7c8fdbd on the
task branch). The target was the maintainer's idle Hetzner CX11 `lead-1`
(135.181.83.114) — **renamed `kasvimuseo-staging-rehearsal` in Hetzner Cloud
the same day** — wiped and booted from the archived Debian 10 genericcloud
image via rescue mode + `qemu-img convert`. Only sshd listened publicly until
the full rehearsal added nginx; all secrets on it are throwaway.

**DNS (2026-08-09):** `kasvimuseo-staging.vempai.men` + `static.` + `media.`
are A records → 135.181.83.114 in Cloudflare's vempai.men zone, **DNS-only
(proxied: false)** — certbot HTTP-01 and the verify play's TLS checks must hit
the host, not Cloudflare's edge. Working token:
`~/.config/secrets/cloudflare-pages-jutut.env` (`CLOUDFLARE_API_TOKEN`, scoped
to the vempai.men zone). The token in `cloudflare-api.env` (`CF_API_TOKEN`) is
**dead** — Cloudflare answers 9109 "Invalid access token".

**origin/master was pushed current on 2026-08-09**, so any `install.yaml` run
(`pip … state=latest`) now deploys the Django 1.7.11 / photologue 3.0.2 /
no-South stack. Over the un-migrated production dump that risks the South-cut
schema gap — README "Crossing the South cut" is the catch-up the real window
needs first.

**The FULL rehearsal passed on 2026-08-09** (`ok=89 failed=0`, run6.log in
`.dev/rehearsal/` of the task worktree): page 200 over trusted HTTPS, HSTS
`max-age=300` asserted, forged Host → clean 400, all three lineages fresh,
passwords idempotent. It took: (a) the South-cut catch-up — restore
production.sql into the dev cluster, run `db upgrade-photologue` from a
`/tmp/stage4` worktree of fa8ac5f with `KASVIMUSEO_IMAGE=kasvimuseo-dev-stage4`
(image already built), then `app manage migrate`, then
`pg_dump --no-owner --no-acl` → `production-migrated.sql` (now the staging
seed in vars/staging.yml); (b) per-domain certbot lineages; (c) uwsgi role
`state=started` fix. `manage.py migrate` interactively prompts about stale
content types at the end — use `--noinput`.

**Certificate lineage trap, proven live (full rehearsal, 2026-08-09):** a
`certbot_certs` entry with three domains issues ONE lineage named after the
first domain, but `nginx-site.conf.j2` loads
`/etc/letsencrypt/live/<server.domain>/` per server block → nginx cannot
start for `static.`/`media.`. Staging now issues one lineage per name
(three `certbot_certs` entries in `vars/staging.yml`). **Real-window risk:**
if production's `live/` directory does not hold per-domain lineages, the
window's nginx-template deploy fails the same way — check on production
before the window (the verify play's 071 certificate task reads exactly
those paths). Buster's certbot 0.31 still issues from Let's Encrypt fine.

**State for the follow-up, in `/home/agent/prg/kasvimuseo/.dev/rehearsal/`:**
`secrets.env` (VP = vault password for the untracked
`ansible/host_vars/staging-rehearsal`, SK/DB/AP = the throwaway secrets, BP =
the kasvimuseo become password), `become-pass` (BP in a file for
`--become-password-file`), `known_hosts` (lead-1 + github host keys), and a
copy of the vaulted `staging-rehearsal` host_vars file.

**The invocation that works** (from the repo root; ansible 9 = core 2.16, the
last line that speaks to Python-2-era targets; gogo's uv config forbids
python downloads, hence the two UV vars):

    source .dev/rehearsal/secrets.env
    UV_PYTHON_PREFERENCE=managed UV_PYTHON_DOWNLOADS=automatic \
    ANSIBLE_VAULT_PASS="$VP" \
    uvx --python 3.12 --from 'ansible==9.*' ansible-playbook \
      -i ansible/hosts.staging -e @ansible/vars/staging.yml \
      -e nginx_start=false --skip-tags nginx,certbot,https \
      --become-password-file .dev/rehearsal/become-pass \
      ansible/secure-production.yaml

For the full rehearsal drop `-e nginx_start=false --skip-tags ...`, point a
real DNS name (+ `static.`/`media.` subdomains) at the host, and set it as
`staging_domain` in `ansible/vars/staging.yml`. Ansible may need
`ANSIBLE_SSH_ARGS='-o UserKnownHostsFile=.dev/rehearsal/known_hosts'` if the
host key is not in the account's default known_hosts. The hcloud token is in
`~/.config/hcloud/cli.toml` (context `kasvimuseo-rehearsal`), written by the
maintainer; `~/.ssh/id_rsa` is the rehearsal keypair (root@lead-1 and
kasvimuseo@lead-1 both accept it; it is also a read-only GitHub deploy key on
akaihola/kasvimuseo). See [[asking-the-maintainer-may-not-land]] for how the
go-ahead arrived, and [[running-ansible-from-this-checkout]].
