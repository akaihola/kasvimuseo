build-app:
	cd .. && \
	podman build \
	  -v $$(pwd)/cache:/root/.cache \
	  -t kasvimuseo \
	  .

build-db:
	cd db && \
	podman build \
	  -t kasvimuseo-postgres \
	  .

build: build-app build-db

run-app:
	podman run \
	  --rm \
	  -p 8000:8000/tcp \
	  --name=kasvimuseo \
	  -e KASVIMUSEO_DEBUG=1 \
	  kasvimuseo

run-db:
	podman run \
	  --rm \
	  --name=kasvimuseo-postgres \
	  kasvimuseo-postgres

shell:
	podman run -it kasvimuseo sh
