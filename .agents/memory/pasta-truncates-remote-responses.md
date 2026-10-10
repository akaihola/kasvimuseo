# Check container port forwarding

This note helps contributors investigate HTTP responses that truncate only for remote clients.

Compare the complete response through the published container port with a connection that bypasses port forwarding.
A local loopback request might not reproduce a failure seen by a remote client.
Check response lengths and server logs before attributing the failure to the application.

[Issue 044](../../docs/issues/044-large-responses-can-truncate-through-container-networking.rst) records the original investigation.
Rootless Podman port forwarding was the cause in that investigation.
Use the current development helper's network configuration when reproducing it.
