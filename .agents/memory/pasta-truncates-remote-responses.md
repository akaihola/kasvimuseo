---
name: pasta-truncates-remote-responses
description: "On gogo, rootless podman's published ports (pasta) truncate mid-size HTTP responses to remote clients; loopback never shows it"
metadata: 
  node_type: memory
  type: project
  originSessionId: f81b28b1-0608-43d2-b47a-0f01c062a1ab
  modified: 2026-07-31T05:00:29.876Z
---

A container port published by rootless podman on `gogo` (`-p 8000:8000`, forwarded
by pasta) delivers about 43 KB of a response to a **remote** client and then closes
the connection cleanly -- the FIN rides the last data segment, every earlier segment
acknowledged, nothing retransmitted. Responses small enough to be forwarded before
the application closes survive, and so do ones too large to buffer, so it presents
as a size *band* rather than a threshold. Confirmed 2026-07-31 (kasvimuseo issue
044): 8 of 10 fetches cut at the identical byte through a published port, 10 of 10
whole with `--network=host`.

**Why:** the loopback baseline is worthless here. A local client acknowledges at
memory speed, so nothing is ever outstanding when the application closes and the
bug cannot appear -- a fast read, a slow read, a 4 KB `SO_RCVBUF`, an eight-second
stall and a request to the host's own tailnet address all delivered every byte.

**How to apply:** when a containerised dev server on `gogo` looks fine locally but
truncates for a remote browser, suspect the port publication before the app, the
network or the MTU. `--network=host` removes the forwarder. An SSH tunnel also
avoids it, by making the remote request a loopback one on the server side. See
[[run-the-suite-in-the-container]] for the podman/sandbox mechanics.
